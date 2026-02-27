"""
swarm_orchestrator.py - Main orchestrator for agent swarm operations.
"""

import asyncio
from datetime import datetime
from typing import Any

from lxml import etree as ET

from src.llm_client import LLMClient
from src.logger import get_logger
from src.project import Project
from src.swarm.agent_role import AgentRole
from src.swarm.swarm_agent import SwarmAgent
from src.swarm.task import Task, TaskPool, TaskType

logger = get_logger(__name__)


class SwarmOrchestrator:
    """
    Orchestrates agent swarm for parallel fiction generation.

    Based on Ultrawork model: Task decomposition -> shared pool -> parallel execution.
    """

    def __init__(
        self,
        project: Project,
        llm_client: LLMClient,
        max_parallel_agents: int = 5,
        max_parallel_chapters: int = 3,
    ):
        self.project = project
        self.llm_client = llm_client
        self.max_parallel_agents = max_parallel_agents
        self.max_parallel_chapters = max_parallel_chapters
        self.task_pool = TaskPool()
        self.agents: list[SwarmAgent] = []
        self.created_at = datetime.now()

    async def run_outline_generation_swarm(self) -> bool:
        """
        Generate outline using agent swarm.

        Deploys: Architect (planning) -> Outliner (generation) -> QA (validation)
        """
        from src.swarm.specialized_agents import (
            ArchitectAgent,
            OutlinerAgent,
            QualityAssuranceAgent,
        )

        logger.info("Starting outline generation with agent swarm")

        # Task 1: Architect decomposes the outline task
        architect_task = Task(
            task_type=TaskType.DECOMPOSE_PROJECT,
            description="Analyze prompt and create outline generation plan",
            priority=0,
            context={},
        )
        await self.task_pool.add_task(architect_task)

        # Task 2: Outliner generates the outline (depends on architect)
        outliner_task = Task(
            task_type=TaskType.GENERATE_OUTLINE,
            description="Generate story outline with chapters and summaries",
            priority=0,
            dependencies=[architect_task.task_id],
            context={},
        )
        await self.task_pool.add_task(outliner_task)

        # Task 3: QA validates the outline
        qa_task = Task(
            task_type=TaskType.VALIDATE_CONTENT,
            description="Validate outline completeness and quality",
            priority=0,
            dependencies=[outliner_task.task_id],
            context={"target_type": "outline"},
        )
        await self.task_pool.add_task(qa_task)

        # Deploy specialized agents
        await self._deploy_agents(
            [
                ArchitectAgent(self.llm_client, self.task_pool, self.project),
                OutlinerAgent(self.llm_client, self.task_pool, self.project),
                QualityAssuranceAgent(self.llm_client, self.task_pool, self.project),
            ]
        )

        # Wait for completion
        success = await self._run_until_complete()

        if success:
            # Extract outline from outliner task result
            outliner = await self.task_pool.get_task(outliner_task.task_id)
            if outliner and outliner.result:
                self.project.apply_patch(outliner.result)
                logger.info("Outline generation complete")
                return True

        logger.error("Outline generation failed")
        return False

    async def run_content_generation_swarm(self) -> bool:
        """
        Generate chapter content using agent swarm.

        Deploys: Multiple Writer agents working in parallel + QA for validation.
        """
        from src.swarm.specialized_agents import QualityAssuranceAgent, WriterAgent

        logger.info("Starting content generation with agent swarm")

        # Get all chapters from outline
        book_root = self.project.book_root
        if book_root is None:
            logger.error("No book root found")
            return False

        chapters = book_root.findall(".//chapter")
        if not chapters:
            logger.error("No chapters found in outline")
            return False

        tasks_created = []

        # Create write tasks for each chapter
        for chapter in chapters:
            chapter_id = chapter.get("id", "")
            title = chapter.find("title")
            title_text = title.text if title is not None else f"Chapter {chapter_id}"

            # Skip if already has content
            paragraphs = chapter.findall(".//paragraph")
            if paragraphs:
                logger.info(f"Skipping chapter {chapter_id} - already has content")
                continue

            # Create write task
            write_task = Task(
                task_type=TaskType.WRITE_CHAPTER,
                description=f"Write content for {title_text}",
                priority=1,
                context={
                    "chapter_id": chapter_id,
                    "book_root": ET.tostring(book_root, encoding="unicode"),
                },
            )
            task_id = await self.task_pool.add_task(write_task)
            tasks_created.append(task_id)

            # Create QA task for this chapter (depends on write)
            qa_task = Task(
                task_type=TaskType.CHECK_QUALITY,
                description=f"Validate quality of {title_text}",
                priority=2,
                dependencies=[task_id],
                context={
                    "chapter_id": chapter_id,
                    "target_type": "chapter",
                },
            )
            await self.task_pool.add_task(qa_task)

        if not tasks_created:
            logger.info("All chapters already have content")
            return True

        # Deploy writer agents (multiple for parallelism)
        agents_to_deploy: list[SwarmAgent] = [
            WriterAgent(self.llm_client, self.task_pool, self.project)
            for _ in range(min(self.max_parallel_chapters, len(tasks_created)))
        ]
        # Add QA agent
        agents_to_deploy.append(
            QualityAssuranceAgent(self.llm_client, self.task_pool, self.project)
        )

        await self._deploy_agents(agents_to_deploy)

        # Run until complete
        success = await self._run_until_complete()

        logger.info(f"Content generation complete. Success: {success}")
        return success

    async def run_editing_swarm(self, chapter_id: str, operation: str) -> bool:
        """
        Run editing operation using agent swarm.

        Args:
            chapter_id: ID of chapter to edit
            operation: 'expand', 'rewrite', or 'enhance'
        """
        from src.swarm.specialized_agents import EditorAgent, QualityAssuranceAgent

        logger.info(f"Starting editing swarm: {operation} for chapter {chapter_id}")

        # Map operation to task type
        task_type_map = {
            "expand": TaskType.EXPAND_CHAPTER,
            "rewrite": TaskType.REWRITE_CHAPTER,
            "enhance": TaskType.EDIT_CHAPTER,
        }

        task_type = task_type_map.get(operation, TaskType.EDIT_CHAPTER)

        # Create editing task
        edit_task = Task(
            task_type=task_type,
            description=f"{operation.capitalize()} chapter {chapter_id}",
            priority=0,
            context={
                "chapter_id": chapter_id,
                "operation": operation,
            },
        )
        await self.task_pool.add_task(edit_task)

        # Create QA task
        qa_task = Task(
            task_type=TaskType.CHECK_QUALITY,
            description=f"Validate edited chapter {chapter_id}",
            priority=1,
            dependencies=[edit_task.task_id],
            context={
                "chapter_id": chapter_id,
                "target_type": "edited_chapter",
            },
        )
        await self.task_pool.add_task(qa_task)

        # Deploy agents
        await self._deploy_agents(
            [
                EditorAgent(self.llm_client, self.task_pool, self.project),
                QualityAssuranceAgent(self.llm_client, self.task_pool, self.project),
            ]
        )

        success = await self._run_until_complete()
        logger.info(f"Editing complete. Success: {success}")
        return success

    async def _deploy_agents(self, agents: list[SwarmAgent]) -> None:
        """Deploy and start agents."""
        self.agents = agents
        for agent in self.agents:
            # Start each agent in a separate task
            asyncio.create_task(agent.start())
            logger.info(f"Deployed agent: {agent.agent_id} ({agent.role.value})")

    async def _run_until_complete(self, timeout: int = 300) -> bool:
        """
        Run agents until all tasks complete or timeout.

        Returns:
            True if all tasks completed successfully, False otherwise.
        """
        start_time = datetime.now()

        while True:
            # Check if complete
            if await self.task_pool.is_complete():
                stats = await self.task_pool.get_stats()
                logger.info(f"All tasks complete. Stats: {stats}")

                # Stop all agents
                for agent in self.agents:
                    await agent.stop()

                # Return success if no failed tasks
                return stats.get("failed", 0) == 0

            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout:
                logger.error(f"Swarm execution timed out after {timeout} seconds")
                for agent in self.agents:
                    await agent.stop()
                return False

            # Small delay
            await asyncio.sleep(0.5)

    async def get_stats(self) -> dict[str, Any]:
        """Get swarm statistics."""
        task_stats = await self.task_pool.get_stats()

        agent_stats = [agent.get_stats() for agent in self.agents]

        return {
            "created_at": self.created_at.isoformat(),
            "max_parallel_agents": self.max_parallel_agents,
            "active_agents": len(self.agents),
            "task_stats": task_stats,
            "agent_stats": agent_stats,
        }
