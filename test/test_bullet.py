#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for bullet integration.
Run this script interactively to test the bullet menu system.
"""

from src.ui import bullet_choice

def main():
    print("Testing bullet integration...")
    
    # Test 1: Simple choice
    print("\n=== Test 1: Simple Choice ===")
    result = bullet_choice('Choose a fruit:', ['Apple', 'Banana', 'Orange', 'Watermelon'])
    print(f'You selected: {result}\n')
    
    # Test 2: Story type selection (mimicking the actual UI)
    print("\n=== Test 2: Story Type Selection ===")
    choice = bullet_choice(
        "Choose project type:",
        ["Novel", "Short Story"]
    )
    story_type = "novel" if choice == "Novel" else "short_story"
    print(f'Project type: {story_type}\n')
    
    # Test 3: Menu with numbers (mimicking lorebook menu)
    print("\n=== Test 3: Numbered Menu ===")
    choice = bullet_choice(
        "Choose an option:",
        [
            "1. Create a new lorebook",
            "2. Import from TavernAI/SillyTavern lorebook",
            "3. Use existing Fiction Fabricator lorebook",
            "4. Skip lorebook setup"
        ]
    )
    choice_num = choice[0]  # Get the first character (the number)
    print(f'Selected option number: {choice_num}\n')
    
    print("All tests completed successfully!")

if __name__ == "__main__":
    main()
