from src.llmconnection import call_g4f_api
from src.prompts import get_title_prompt


def generate_title(updated_synopsis, genre, style, tone, pov, premise):
    """
    Generates a title for the novel based on the updated synopsis using the OpenAI API.
    """

    prompt = get_title_prompt(updated_synopsis, genre, style, tone, pov, premise)
    response = call_g4f_api(prompt)
    title = response
    return title
