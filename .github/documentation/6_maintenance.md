# 6. Maintenance

This section covers scripts and tools designed to help keep your project directory clean and organized.

## Cleaning Caches and Logs (`.github/Functions/tidy_up.sh`)

Over time, running Fiction Fabricator will generate numerous log files and Python caches (`__pycache__`). To help manage this, a cleanup script is provided.

### What it Does:

The script performs the following actions:
-   Finds and recursively deletes all `__pycache__` directories from the project root.
-   Removes the entire `Logs/` directory and all its contents. This includes all run-specific logs, debug files, and temporary generation artifacts.

**Important:** This script is designed to *only* remove logs and cache files. It will **not** remove your generated stories in `Generated_Content/` or your custom Lorebooks in `LoreBooks/`.

### How to Use:

Execute the script from the root of the project directory.

```bash
bash .github/Functions/tidy_up.sh
```

This will tidy up your workspace, which is especially useful before archiving the project or when you want to clear out old test runs.
