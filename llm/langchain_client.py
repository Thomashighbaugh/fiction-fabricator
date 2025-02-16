# llm/langchain_client.py
from typing import Dict, Any

from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.logger import logger
from utils.config import config


class LangchainClient:
    """
    Client for interacting with Ollama using Langchain for prompt chaining.
    """

    def __init__(self, model_name: str = None):
        """
        Initializes the Langchain client with an Ollama model.
        """
        if not model_name:
            model_name = config.get_ollama_model_name()

        self.model = Ollama(model=model_name)

    def generate_text(self, prompt: str) -> str | None:
        """
        Generates text using a simple prompt.

        Args:
            prompt (str): The prompt for text generation.

        Returns:
            str | None: The generated text, or None if an error occurred.
        """
        try:
            logger.debug("Prompt being sent to LLM: %s", prompt)
            generated_text = self.model(prompt)
            logger.info("Text generated successfully using Langchain.")
            return generated_text
        except (ValueError, RuntimeError) as e:
            logger.error("Error generating text with Langchain: %s", e)
            return None

    def create_actionable_critique(
        self, content: str, variables: Dict[str, Any], prompt_template: str
    ) -> str | None:
        """
        Generates an actionable critique of the given content using a Langchain chain.

        Args:
            content (str): The content to be critiqued.
            variables (Dict[str, Any]): A dictionary of variables to be used in the prompt.
            prompt_template (str): The prompt template for generating the critique.

        Returns:
            str | None: The actionable critique, or None if an error occurred.
        """
        try:
            prompt = PromptTemplate(
                input_variables=list(variables.keys()),
                template=prompt_template,
            )
            chain = LLMChain(llm=self.model, prompt=prompt)
            all_variables = variables.copy()
            all_variables["content"] = content  # Add content to variables
            logger.debug("Variables being sent to critique chain: %s", all_variables)
            critique = chain.run(**all_variables)
            logger.info("Actionable critique generated successfully using Langchain.")
            return critique
        except (ValueError, RuntimeError) as e:
            logger.error("Error generating actionable critique with Langchain: %s", e)
            return None

    def rewrite_content(
        self,
        content: str,
        critique: str,
        variables: Dict[str, Any],
        prompt_template: str,
    ) -> str | None:
        """
        Rewrites content based on a critique using a Langchain chain.

        Args:
            content (str): The content to be rewritten.
            critique (str): The actionable critique to guide the rewriting.
            variables (Dict[str, Any]): A dictionary of variables to be used in the prompt.
            prompt_template (str): The prompt template for rewriting the content.

        Returns:
            str | None: The rewritten content, or None if an error occurred.
        """
        try:
            prompt = PromptTemplate(
                input_variables=list(variables.keys()),
                template=prompt_template,
            )
            chain = LLMChain(llm=self.model, prompt=prompt)
            all_variables = variables.copy()
            all_variables["content"] = content
            all_variables["critique"] = critique
            logger.debug("Variables being sent to rewrite chain: %s", all_variables)
            rewritten_content = chain.run(**all_variables)
            logger.info("Content rewritten successfully using Langchain.")
            return rewritten_content
        except (ValueError, RuntimeError) as e:
            logger.error("Error rewriting content with Langchain: %s", e)
            return None
