"""
swarm_agent.py - Base class for all swarm agents.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.llm_client import LLMClient
from src.logger import get_logger
from src.swarm.agent_role import AgentCapability, AgentRole, get_agent_capability
from src.swarm.task import Task, TaskPool, TaskStatus

logger = get_logger(__name__)


class SwarmAgent(ABC):
    """Base class for all swarm agents."""

    def __init__(
        self,
        role: AgentRole,
        llm_client: LLMClient,
        task_pool: TaskPool,
        agent_id: str | None = None,
    ):
        self.role = role
        self.agent_id = agent_id or f"{role.value}-{str(uuid.uuid4())[:8]}"
        self.llm_client = llm_client
        self.task_pool = task_pool
        self.capability = get_agent_capability(role)
        self.active = False
        self.current_tasks: list[str] = []  # IDs of tasks currently being worked on
        self.completed_tasks: list[str] = []
        self.failed_tasks: list[str] = []
        self.created_at = datetime.now()

    async def start(self) -> None:
        """Start the agent's work loop."""
        self.active = True
        logger.info(f"Agent {self.agent_id} ({self.role.value}) started")

        while self.active:
            # Check if we can take on more tasks
            if len(self.current_tasks) < self.capability.max_concurrent_tasks:
                # Get a ready task
                ready_tasks = await self.task_pool.get_ready_tasks(limit=1)
                if ready_tasks:
                    task = ready_tasks[0]
                    # Check if this agent can handle this task
                    if self.can_handle_task(task):
                        # Try to claim it
                        if await self.task_pool.claim_task(task.task_id, self.agent_id):
                            self.current_tasks.append(task.task_id)
                            # Process task asynchronously
                            asyncio.create_task(self._process_task(task))

            # Check if all tasks are complete
            if await self.task_pool.is_complete():
                logger.info(f"Agent {self.agent_id} detected all tasks complete")
                break

            # Small delay to avoid busy waiting
            await asyncio.sleep(0.1)

        logger.info(
            f"Agent {self.agent_id} stopped. Completed: {len(self.completed_tasks)}, Failed: {len(self.failed_tasks)}"
        )

    async def stop(self) -> None:
        """Stop the agent's work loop."""
        self.active = False

    @abstractmethod
    def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle a specific task."""
        pass

    @abstractmethod
    async def process_task(self, task: Task) -> Any:
        """Process a task and return the result. Must be implemented by subclasses."""
        pass

    async def _process_task(self, task: Task) -> None:
        """Internal task processing with error handling."""
        try:
            logger.info(f"Agent {self.agent_id} processing task {task.task_id}: {task.description}")
            result = await self.process_task(task)
            await self.task_pool.complete_task(task.task_id, result)
            self.completed_tasks.append(task.task_id)
            logger.info(f"Agent {self.agent_id} completed task {task.task_id}")
        except Exception as e:
            error_msg = f"Error processing task: {e}"
            logger.error(f"Agent {self.agent_id} failed task {task.task_id}: {error_msg}")
            await self.task_pool.fail_task(task.task_id, error_msg)
            self.failed_tasks.append(task.task_id)
        finally:
            # Remove from current tasks
            if task.task_id in self.current_tasks:
                self.current_tasks.remove(task.task_id)

    async def get_llm_response(self, prompt: str, task_desc: str) -> str | None:
        """Get response from LLM with error handling."""
        try:
            # For now, use synchronous call. Can be enhanced with async later
            return self.llm_client.get_response(prompt, task_desc, allow_stream=False)
        except Exception as e:
            logger.error(f"Agent {self.agent_id} LLM error: {e}")
            return None

    def get_stats(self) -> dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "active": self.active,
            "current_tasks": len(self.current_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "created_at": self.created_at.isoformat(),
        }
