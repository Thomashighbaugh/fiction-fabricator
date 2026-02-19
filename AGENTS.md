# AI Agent Guidelines

- Always update the documentation in `/.documentation` whenever features change or other relevant code, workflow, or architecture changes make the old documentation obsolete. Proactively ensure the documentation remains the single source of truth for the codebase.

## Swarm Architecture and Coordination

To ensure high-quality software delivery at speed, the AI agents in this project operate in a simultaneous, cohesive "swarm-like" configuration. All agents adhere to specific, bounded roles and coordinate their efforts through a centralized orchestrator.

### 1. Centralized Coordination (The Orchestrator)
- **Role:** The **Central Coordinator** is responsible for breaking down high-level user requests into atomic, actionable subtasks.
- **Responsibilities:** 
  - Evaluate the codebase context and decompose epics into parallelizable units of work.
  - Spawn specialized worker agents for each subtask.
  - Maintain the global state of the objective and broadcast context updates when relevant changes occur across the swarm.
  - Review, verify, and merge completed subtasks back into the main workflow.

### 2. Specialized Worker Roles
Worker agents operate simultaneously and autonomously within their specific domains. They do not overstep their boundaries and rely on the Orchestrator for broader context.

- **Backend / API Developer:** Focuses purely on data models, business logic, endpoints, database schema changes, and service integrations.
- **Frontend / UI Developer:** Focuses strictly on user interfaces, component design, styling, and client-side state management.
- **Code Reviewer / Quality Assurance (QA):** Acts as an adversarial gatekeeper. Validates logic, ensures adherence to project standards, writes/runs tests, and checks for security vulnerabilities before any code is approved for merging.
- **Documentation / Technical Writer:** Dedicated to maintaining the `.documentation` folder, updating READMEs, and ensuring inline code documentation is clear and accurate.

### 3. Execution Workflow
1. **Isolated Workspaces:** Each worker agent operates in an isolated environment (e.g., a git worktree or reserved file paths) to prevent conflicts while running simultaneously.
2. **Asynchronous Progress Updates:** Workers must regularly report their status (`in_progress`, `blocked`, `completed`, `failed`) to the Central Coordinator.
3. **Cross-Agent Communication:** If a worker's task impacts another (e.g., an API payload change affecting the Frontend Developer), the worker signals the Central Coordinator, which broadcasts the update to the relevant agents.
4. **Verification Gate:** No subtask is considered complete until it passes type-checking, automated tests, and adversarial review by the QA agent. Once approved, the Orchestrator merges the changes.
