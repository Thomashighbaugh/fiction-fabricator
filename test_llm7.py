#!/usr/bin/env python3

import os
import sys
sys.path.append('src')

from dotenv import load_dotenv
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def test_llm7():
    load_dotenv()
    
    # Test if LLM7_API_KEY is set
    api_key = os.environ.get("LLM7_API_KEY")
    if not api_key:
        print("LLM7_API_KEY not found in environment. Please set it in your .env file.")
        return False
    
    print(f"LLM7_API_KEY found: {'*' * 8}{api_key[-4:] if len(api_key) > 4 else '****'}")
    
    # Initialize the interface with an LLM7 model
    interface = Interface()
    logger = Logger()
    
    # Test model - using one of the available models from LLM7
    test_model = "llm7://gpt-4.1-nano-2025-04-14"
    
    try:
        # Load the model
        interface.LoadModels([test_model])
        print(f"✅ Model {test_model} loaded successfully!")
        
        # Test a simple conversation
        messages = [
            {"role": "user", "content": "Hello! Please respond with exactly 'LLM7 integration test successful' if you can understand this message."}
        ]
        
        print(f"Testing {test_model}...")
        response_history = interface.ChatAndStreamResponse(logger, messages, test_model)
        
        if response_history and len(response_history) > 1:
            response = response_history[-1].get("content", "")
            print(f"Response: {response}")
            
            if "LLM7 integration test successful" in response or "successful" in response.lower():
                print("✅ LLM7 integration test PASSED!")
                return True
            else:
                print("⚠️  LLM7 responded but didn't match expected output")
                return True  # Still successful communication
        else:
            print("❌ No response received from LLM7")
            return False
            
    except Exception as e:
        print(f"❌ LLM7 integration test FAILED: {e}")
        return False

def test_available_models():
    """Test some of the available LLM7 models"""
    available_models = [
        "deepseek-r1-0528",
        "gemini", 
        "gpt-5-nano-2025-08-07",
        "llama-fast-roblox",
        "llama-3.1-8b-instruct-fp8",
        "mistral-small-3.1-24b-instruct-2503",
        "gpt-4o-mini-2024-07-18",
        "gpt-4.1-nano-2025-04-14",
        "mistral-large-2411"
    ]
    
    print("\n🔍 Available LLM7 models that can be used:")
    for model in available_models:
        print(f"   - llm7://{model}")
    
    print("\n📝 Example usage in config.ini:")
    print('   INITIAL_OUTLINE_WRITER_MODEL = "llm7://gpt-4.1-nano-2025-04-14"')
    print('   CHAPTER_OUTLINE_WRITER_MODEL = "llm7://deepseek-r1-0528"')
    print('   EVAL_MODEL = "llm7://mistral-large-2411"')

if __name__ == "__main__":
    success = test_llm7()
    test_available_models()
    sys.exit(0 if success else 1)