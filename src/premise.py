# fiction-fabricator/src/premise.py
from src.llmconnection import call_g4f_api
from src.prompts import get_premise_prompt


def generate_premises():
    """
    Prompts the user for input and generates 5 potential novel premises.
    """
    user_input = input(
        "Enter a few keywords, a brief description, or a theme to inspire novel premises: "
    )

    prompt = get_premise_prompt(user_input)
    response = call_g4f_api(prompt)

    premises = response.split("\n")  # Assuming each premise is on a separate line
    print("Potential Novel Premises:")
    for i, premise in enumerate(premises, 1):
        if premise.strip():  # Skip empty lines
            print(f"{i}. {premise.strip()}")

    print("\nPlease copy and paste your chosen premise into the next prompt.")
