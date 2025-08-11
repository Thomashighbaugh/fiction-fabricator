import argparse
import json
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def evaluate_stories(story1_path, story2_path, output_path, model):
    """
    Evaluates two stories using an LLM.
    """
    logger = Logger("Evaluate")

    try:
        with open(story1_path, 'r', encoding='utf-8') as f:
            story1_data = json.load(f)
        with open(story2_path, 'r', encoding='utf-8') as f:
            story2_data = json.load(f)
    except FileNotFoundError as e:
        logger.Log(f"Error: {e}. One of the story files was not found.", 7)
        return
    except json.JSONDecodeError as e:
        logger.Log(f"Error decoding JSON from a story file: {e}", 7)
        return

    story1_text = story1_data.get("Full_Story", "")
    story2_text = story2_data.get("Full_Story", "")

    if not story1_text or not story2_text:
        logger.Log("Error: One of the stories is empty. Cannot evaluate.", 7)
        return

    logger.Log(f"Evaluating stories using model: {model}", 4)

    llm_interface = Interface(Models=[model])

    prompt = f"""
    You are a literary critic. You will be given two short stories. Your task is to evaluate them based on the following criteria:
    1.  **Coherence and Plot:** How well-structured is the story? Is the plot engaging and logical?
    2.  **Character Development:** Are the characters believable and well-developed?
    3.  **Prose and Style:** How is the quality of the writing? Is the style consistent and effective?
    4.  **Originality and Creativity:** How original is the story's concept and execution?
    5.  **Overall Impression:** Your final thoughts and which story you think is better and why.

    Please provide a detailed analysis for each story based on these criteria, and then a final verdict.

    **Story 1:**
    ---
    {story1_text}
    ---

    **Story 2:**
    ---
    {story2_text}
    ---
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant and literary critic."},
        {"role": "user", "content": prompt}
    ]

    response_history = llm_interface.ChatAndStreamResponse(logger, messages, model)
    evaluation_text = llm_interface.GetLastMessageText(response_history)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(evaluation_text)
        logger.Log(f"Evaluation report saved to {output_path}", 5)
    except IOError as e:
        logger.Log(f"Error writing evaluation report to file: {e}", 7)

if __name__ == "__main__":
    # Setup Argparser
    Parser = argparse.ArgumentParser(description="Evaluate and compare two generated stories.")
    Parser.add_argument("-Story1", required=True, help="Path to JSON file for story 1")
    Parser.add_argument("-Story2", required=True, help="Path to JSON file for story 2")
    Parser.add_argument("-Output", default="Report.md", type=str, help="Optional file output path for the report.")
    Parser.add_argument("-Model", default="google://gemini-1.5-pro-latest", type=str, help="Model to use for the evaluation.")
    Args = Parser.parse_args()
    evaluate_stories(Args.Story1, Args.Story2, Args.Output, Args.Model)
