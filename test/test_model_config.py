#!/usr/bin/env python3
"""
Test script to verify the model configuration change.
"""

def test_model_configuration():
    """Test that the model is correctly configured."""

    from src.config import WRITING_MODEL_NAME, WRITING_MODEL_CONFIG

    print("Testing model configuration...")
    print(f"✓ Model name: {WRITING_MODEL_NAME}")
    print(f"✓ Temperature: {WRITING_MODEL_CONFIG.temperature}")
    print(f"✓ Max tokens: {WRITING_MODEL_CONFIG.max_output_tokens}")
    print(f"✓ Top P: {WRITING_MODEL_CONFIG.top_p}")
    print(f"✓ Top K: {WRITING_MODEL_CONFIG.top_k}")

    # Verify it's the expected model
    expected_model = "gemini-2.5-flash"
    if WRITING_MODEL_NAME == expected_model:
        print(f"✅ Model correctly set to {expected_model}")
    else:
        print(f"❌ Model mismatch! Expected {expected_model}, got {WRITING_MODEL_NAME}")
        return False

    # Verify token limit is appropriate
    if WRITING_MODEL_CONFIG.max_output_tokens == 65536:
        print("✅ Token limit correctly set to 65,536")
    else:
        print(f"⚠️  Token limit is {WRITING_MODEL_CONFIG.max_output_tokens}, expected 65,536")

    print("\n🎉 Model configuration test passed!")
    return True

if __name__ == "__main__":
    test_model_configuration()