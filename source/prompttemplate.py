# Explanation:
# I have made the following changes to improve the code:
# 1. Added a type hint for the argument 'template_id'.
# 2. Added a return type hint for the function.
# 3. Added error handling in case the template file is not found.
# 4. Renamed the function 'get' to 'get_template' for clarity.
# 5. Added a docstring to describe the function.

import os

class PromptTemplate:

    def get_template(template_id: str) -> str:
        """
        Get the prompt template based on the template ID.

        Args:
            template_id (str): The ID of the template to retrieve.

        Returns:
            str: The content of the template file.
        """

        template_path = os.path.join("prompt_templates", template_id + ".txt")
        try:
            with open(template_path, "r") as f:
                template = f.read()
            return template
        except FileNotFoundError:
            print(f"Template file '{template_path}' not found.")
            return ""
