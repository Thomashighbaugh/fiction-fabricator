# 2. Installation Guide

This guide provides everything you need to know to install the project and set up its dependencies.

## Prerequisites

- Python 3.10 or higher.
- `git` for cloning the repository.

## Installation Steps

Follow these steps from your terminal to get the project running.

```bash
# 1. Clone the repository
# Replace <your-repository-url> with the actual URL of the project repository
git clone <your-repository-url>

# 2. Navigate into the project directory
cd fiction-fabricator # Or your project's root directory name

# 3. (Recommended) Create and activate a virtual environment
# This isolates the project's dependencies from your system's Python installation.
python -m venv venv

# Activate the virtual environment:
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 4. Install the required packages
# The requirements.txt file contains all necessary Python libraries.
pip install -r requirements.txt
```

Once these steps are complete, the application is installed and you can proceed to the configuration step.
