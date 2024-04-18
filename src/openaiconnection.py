import g4f

def call_openai_api(prompt):
    """
    Calls the GPT4Free API with the provided prompt and system message.

    Args:
        prompt: The prompt to send to the API.
        system_message: The system message for prompting the AI.

    Returns:
        The generated text from the GPT4Free API.
    """

    api_instance = g4f.ChatCompletion()

        # Call the API with the specified parameters
    response = api_instance.create(
            model="mixtral-8x7b",  # Use the 'mistral-7b' model
            messages=[{"role": "system", "content": prompt}],
        )

        # Extract and return the generated text
    generated_text = response
    print(generated_text)
    return generated_text

# import google.generativeai as genai
# import os

# Placeholder for the environmental variable holding the value for the key

# GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

# genai.configure(api_key=GOOGLE_API_KEY)


# Define a single function to interact with the OpenAI API
# def call_openai_api(prompt):
    """
    Calls the Gemini API (I will rename it one day) with the provided prompt and system message.

    Args:
        prompt: The prompt to send to the API.
        system_message: The system message for prompting the AI.

    Returns:
        The response from the OpenAI API.
    """

    # Set up the model
#   generation_config = {
#       "temperature": 1.4,
#       "top_p": 1,
#       "top_k": 1,
#       "max_output_tokens": 2048,
#   }

#   model = genai.GenerativeModel(
#       model_name="gemini-1.0-pro-latest",
#       generation_config=generation_config,
#       safety_settings=[
#           {
#               "category": "HARM_CATEGORY_HARASSMENT",
#               "threshold": "BLOCK_NONE",
#           },
#           {
#               "category": "HARM_CATEGORY_HATE_SPEECH",
#               "threshold": "BLOCK_NONE",
#           },
#           {
#               "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#               "threshold": "BLOCK_NONE",
#           },
#           {
#               "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#               "threshold": "BLOCK_NONE",
#           },
#       ],
#   )
#   response = model.generate_content(prompt)
#   generated_text = response.text
#   print(generated_text)
#   return generated_text































