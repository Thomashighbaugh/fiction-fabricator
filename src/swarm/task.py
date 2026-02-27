"""
task.py - Task definitions and task pool management for agent swarm.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Status of a task in the pool."""

    PENDING = "pending"  # Waiting for dependencies
    READY = "ready"  # Ready to be claimed by an agent
    CLAIMED = "claimed"  # Claimed by an agent, work in progress
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed after retries
    BLOCKED = "blocked"  # Blocked by external factors


class TaskType(Enum):
    """Types of tasks that can be performed."""

    # Planning Tasks
    DECOMPOSE_PROJECT = "decompose_project"
    GENERATE_OUTLINE = "generate_outline"
    PLAN_CHAPTERS = "plan_chapters"

    # Content Generation Tasks
    WRITE_CHAPTER = "write_chapter"
    WRITE_DIALOGUE = "write_dialogue"
    WRITE_DESCRIPTION = "write_description"
    WRITE_ACTION = "write_action"

    # Editing Tasks
    EDIT_CHAPTER = "edit_chapter"
    EXPAND_CHAPTER = "expand_chapter"
    REWRITE_CHAPTER = "rewrite_chapter"

    # Quality Tasks
    VALIDATE_CONTENT = "validate_content"
    CHECK_CONTINUITY = "check_continuity"
    CHECK_QUALITY = "check_quality"
    FIX_XML_ERROR = "fix_xml_error"

    # Support Tasks
    MANAGE_LOREBOOK = "manage_lorebook"
    UPDATE_CHARACTER = "update_character"


@dataclass
class Task:
    """Represents a single work item in the swarm."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.WRITE_CHAPTER
    description: str = ""
    priority: int = 2  # 0=highest, 4=lowest
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)  # IDs of tasks that must complete first
    assigned_agent: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    claimed_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    context: dict[str, Any] = field(default_factory=dict)  # Task-specific data
    result: Any = None
    error: str | None = None

    def can_be_claimed(self, completed_task_ids: set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        if self.status != TaskStatus.PENDING:
            return False
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def claim(self, agent_id: str) -> None:
        """Mark task as claimed by an agent."""
        self.status = TaskStatus.CLAIMED
        self.assigned_agent = agent_id
        self.claimed_at = datetime.now()

    def complete(self, result: Any) -> None:
        """Mark task as successfully completed."""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = TaskStatus.FAILED
            self.error = error
        else:
            # Reset to pending for retry
            self.status = TaskStatus.PENDING
            self.assigned_agent = None
            self.error = error


class TaskPool:
    """Thread-safe task pool for managing work distribution across agents."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._completed_task_ids: set[str] = set()

    async def add_task(self, task: Task) -> str:
        """Add a task to the pool."""
        async with self._lock:
            self.tasks[task.task_id] = task
            # If no dependencies, mark as ready
            if not task.dependencies:
                task.status = TaskStatus.READY
            return task.task_id

    async def add_tasks(self, tasks: list[Task]) -> list[str]:
        """Add multiple tasks to the pool."""
        task_ids = []
        for task in tasks:
            task_id = await self.add_task(task)
            task_ids.append(task_id)
        return task_ids

    async def get_ready_tasks(self, limit: int | None = None) -> list[Task]:
        """Get tasks that are ready to be claimed."""
        async with self._lock:
            # Update task statuses based on completed dependencies
            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING and task.can_be_claimed(
                    self._completed_task_ids
                ):
                    task.status = TaskStatus.READY

            # Get ready tasks sorted by priority
            ready_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.READY]
            ready_tasks.sort(key=lambda t: (t.priority, t.created_at))

            if limit:
                return ready_tasks[:limit]
            return ready_tasks

    async def claim_task(self, task_id: str, agent_id: str) -> bool:
        """Claim a task for an agent."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.READY:
                return False

            task.claim(agent_id)
            return True

    async def complete_task(self, task_id: str, result: Any) -> bool:
        """Mark a task as completed."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return False

            task.complete(result)
            self._completed_task_ids.add(task_id)
            return True

    async def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return False

            task.fail(error)
            return True

    async def get_task(self, task_id: str) -> Task | None:
        """Get a specific task by ID."""
        async with self._lock:
            return self.tasks.get(task_id)

    async def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        async with self._lock:
            return list(self.tasks.values())

    async def get_stats(self) -> dict[str, int]:
        """Get statistics about the task pool."""
        async with self._lock:
            stats = {
                "total": len(self.tasks),
                "pending": 0,
                "ready": 0,
                "claimed": 0,
                "completed": 0,
                "failed": 0,
                "blocked": 0,
            }

            for task in self.tasks.values():
                stats[task.status.value] += 1

            return stats

    async def is_complete(self) -> bool:
        """Check if all tasks are completed or failed."""
        async with self._lock:
            return all(
                t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED) for t in self.tasks.values()
            )
