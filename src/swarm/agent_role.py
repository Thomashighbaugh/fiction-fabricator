"""
agent_role.py - Defines specialized agent roles for the fiction generation swarm.
"""

from enum import Enum


class AgentRole(Enum):
    """Defines the specialized roles that agents can take in the swarm."""

    # Planning & Design Agents
    ARCHITECT = "architect"  # Breaks down tasks and designs overall structure
    OUTLINER = "outliner"  # Generates outlines, character profiles, summaries
    PLANNER = "planner"  # Plans chapter sequences and narrative flow

    # Content Generation Agents
    WRITER = "writer"  # Generates prose content for chapters
    DIALOGUE_SPECIALIST = "dialogue_specialist"  # Focuses on character dialogue
    DESCRIPTION_SPECIALIST = "description_specialist"  # Focuses on descriptive passages
    ACTION_SPECIALIST = "action_specialist"  # Focuses on action sequences

    # Quality & Enhancement Agents
    EDITOR = "editor"  # Edits and refines existing content
    CONTINUITY_CHECKER = "continuity_checker"  # Ensures plot and character consistency
    QUALITY_ASSURANCE = "qa"  # Validates output quality and completeness
    STYLE_ENHANCER = "style_enhancer"  # Improves prose style and flow

    # Specialized Support Agents
    LOREBOOK_MANAGER = "lorebook_manager"  # Manages world-building and context
    CHARACTER_MANAGER = "character_manager"  # Manages character consistency
    BUILD_FIXER = "build_fixer"  # Fixes XML parsing errors and structural issues

    # Coordination Agents
    ORCHESTRATOR = "orchestrator"  # Main coordination agent
    VALIDATOR = "validator"  # Validates task completion against requirements


class AgentPriority(Enum):
    """Priority levels for task execution."""

    CRITICAL = 0  # Must be done first (blocking tasks)
    HIGH = 1  # Important tasks that should be done soon
    MEDIUM = 2  # Normal priority tasks
    LOW = 3  # Can be deferred if system is busy
    BACKGROUND = 4  # Run when idle


class AgentCapability:
    """Defines what an agent can do."""

    def __init__(
        self,
        role: AgentRole,
        can_generate_content: bool = False,
        can_edit_content: bool = False,
        can_validate: bool = False,
        can_plan: bool = False,
        max_concurrent_tasks: int = 1,
        preferred_model: str = "default",
    ):
        self.role = role
        self.can_generate_content = can_generate_content
        self.can_edit_content = can_edit_content
        self.can_validate = can_validate
        self.can_plan = can_plan
        self.max_concurrent_tasks = max_concurrent_tasks
        self.preferred_model = preferred_model


# Define capabilities for each agent role
AGENT_CAPABILITIES = {
    AgentRole.ARCHITECT: AgentCapability(
        role=AgentRole.ARCHITECT,
        can_plan=True,
        max_concurrent_tasks=1,
        preferred_model="high_reasoning",
    ),
    AgentRole.OUTLINER: AgentCapability(
        role=AgentRole.OUTLINER,
        can_generate_content=True,
        can_plan=True,
        max_concurrent_tasks=1,
        preferred_model="high_reasoning",
    ),
    AgentRole.WRITER: AgentCapability(
        role=AgentRole.WRITER,
        can_generate_content=True,
        max_concurrent_tasks=3,  # Can write multiple chapters in parallel
        preferred_model="default",
    ),
    AgentRole.EDITOR: AgentCapability(
        role=AgentRole.EDITOR,
        can_edit_content=True,
        max_concurrent_tasks=2,
        preferred_model="default",
    ),
    AgentRole.QUALITY_ASSURANCE: AgentCapability(
        role=AgentRole.QUALITY_ASSURANCE,
        can_validate=True,
        max_concurrent_tasks=1,
        preferred_model="high_reasoning",
    ),
    AgentRole.BUILD_FIXER: AgentCapability(
        role=AgentRole.BUILD_FIXER,
        can_edit_content=True,
        max_concurrent_tasks=1,
        preferred_model="fast",
    ),
}


def get_agent_capability(role: AgentRole) -> AgentCapability:
    """Get capabilities for a specific agent role."""
    return AGENT_CAPABILITIES.get(
        role,
        AgentCapability(role=role, max_concurrent_tasks=1),
    )
