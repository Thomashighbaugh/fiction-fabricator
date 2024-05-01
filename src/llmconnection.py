from gradio_client import Client
def call_g4f_api(prompt):
    """
    Calls the GPT4Free API with the provided prompt and system message.

    Args:
        prompt: The prompt to send to the API.
        system_message: The system message for prompting the AI.

    Returns:
        The generated text from the GPT4Free API.
    """
    client = Client("https://thomashighbaugh-tehvenom-mpt-7b-wizardlm-uncenso-7b47c4c.hf.space/")
        # Call the API with the specified parameters
    response = client.predict(prompt, 
                              api_name="/predict"

        )

        # Extract and return the generated text
    generated_text = response

    return generated_text
