#!/usr/bin/env python3
"""
Simple test for bullet_choice functionality without dependencies.
"""

def test_bullet_choice_logic():
    """Test the bullet choice logic without Rich dependencies."""

    # Simulate the bullet_choice function logic
    choices = ['Apple', 'Banana', 'Orange', 'Watermelon']

    print("Testing bullet_choice logic...")
    print("\nChoose a fruit:")
    print("Use ↑/↓ arrow keys to navigate, Enter to select, or type a number")
    print()

    # Simulate the table display
    for i, choice in enumerate(choices, 1):
        print(f"{i} {choice}")

    print()
    print("Your choice: ", end="")

    # Test with sample input
    test_inputs = ["2", "Banana", "ban", "3", "1", "invalid"]

    for test_input in test_inputs:
        print(f"Testing input: '{test_input}'")

        # Simulate the new logic from bullet_choice
        if test_input.isdigit():
            index = int(test_input) - 1
            if 0 <= index < len(choices):
                result = choices[index]
                print(f"  ✓ Selected: {result}")
            else:
                print("  Please enter a number between 1 and 4")
        else:
            # Check if input matches a choice directly (case-insensitive)
            found = False
            for choice in choices:
                if test_input.lower() == choice.lower():
                    print(f"  ✓ Selected: {choice}")
                    found = True
                    break

            if not found:
                # Try partial matching for convenience
                matches = [choice for choice in choices if test_input.lower() in choice.lower()]
                if len(matches) == 1:
                    print(f"  ✓ Selected: {matches[0]}")
                elif len(matches) > 1:
                    print("  Multiple matches found. Please be more specific or use a number:")
                    for i, match in enumerate(matches, 1):
                        print(f"    {i}. {match}")
                else:
                    print("  No matching option found. Please enter a number (1-4) or type the option name")

        print()

if __name__ == "__main__":
    test_bullet_choice_logic()