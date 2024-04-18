# ideas.py functions (modified)
from src.openaiconnection import call_openai_api
from src.prompts import get_idea_prompt

# ─────────────────────────────────────────────────────────────────


def generate_ideas(genre, style, tone, pov, premise):
    """
    Generates a dictionary of high-concept pitches for the novel.
    """

    prompt = get_idea_prompt(genre, style, tone, pov, premise)
    response = call_openai_api(prompt)

    # Assuming the API returns ideas in a list format
    ideas_list = response.split(
        "\n"
    )  # Or use appropriate parsing based on API response

    ideas_dict = {}
    for i, idea in enumerate(ideas_list):
        ideas_dict[i + 1] = idea  # Assign unique IDs to ideas

    return ideas_dict


def merge_ideas(ideas_dict, idea_ids):
    """
    Merges ideas from the ideas dictionary based on the provided IDs.
    """

    merged_idea = ""
    for idea_id in idea_ids:
        merged_idea += ideas_dict[idea_id] + " "  # Combine idea texts
    return merged_idea.strip()


def modify_idea(ideas_dict, idea_id):
    """
    Modifies an idea in the ideas dictionary.
    """

    new_idea = input("Enter the modified idea: ")
    ideas_dict[idea_id] = new_idea


# ─────────────────────────────────────────────────────────────────
# ideas.py function (for user interaction)
def choose_idea(ideas_dict):
    """
    Presents the generated ideas to the user and allows them to choose one, merge ideas, or modify an idea.
    """

    print("Here are the generated ideas:")
    for i, idea in enumerate(ideas_dict.values(), 1):  # Iterate over values
        print(f"{i}. {idea}")

    while True:
        choice = input(
            "Enter the number of the idea you want to develop, 'merge' to combine ideas, or 'modify' to edit an idea: "
        )
        if choice.isdigit():
            return ideas_dict[int(choice)]
        elif choice.lower() == "merge":
            idea_ids = [
                int(x)
                for x in input(
                    "Enter the IDs of the ideas to merge (separated by spaces): "
                ).split()
            ]
            merged_idea = merge_ideas(ideas_dict, idea_ids)
            print("Merged idea:", merged_idea)
            return merged_idea
        elif choice.lower() == "modify":
            idea_id = int(input("Enter the ID of the idea to modify: "))
            modify_idea(ideas_dict, idea_id)
            print("Modified idea:", ideas_dict[idea_id])
            return ideas_dict[idea_id]
        else:
            print("Invalid choice. Please try again.")
