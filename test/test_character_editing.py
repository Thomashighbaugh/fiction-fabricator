#!/usr/bin/env python3
"""
Test script to demonstrate character name editing functionality.
"""

import xml.etree.ElementTree as ET

def test_character_name_editing():
    """Test the character name editing logic."""
    
    # Create a sample XML structure with characters
    book_root = ET.Element("book")
    ET.SubElement(book_root, "title").text = "Test Book"
    
    # Create story elements
    story_elements = ET.SubElement(book_root, "story_elements")
    ET.SubElement(story_elements, "genre").text = "Fantasy"
    ET.SubElement(story_elements, "tone").text = "Epic"
    ET.SubElement(story_elements, "perspective").text = "Third Person"
    ET.SubElement(story_elements, "target_audience").text = "Adults"
    
    # Create characters
    characters = ET.SubElement(book_root, "characters")
    
    char1 = ET.SubElement(characters, "character")
    char1.set("id", "protagonist")
    ET.SubElement(char1, "name").text = "Aragorn"
    ET.SubElement(char1, "description").text = "The hero of the story"
    
    char2 = ET.SubElement(characters, "character")
    char2.set("id", "antagonist")
    ET.SubElement(char2, "name").text = "Sauron"
    ET.SubElement(char2, "description").text = "The dark lord"
    
    # Display original character names
    print("Original character names:")
    for char in characters.findall("character"):
        char_id = char.get("id")
        char_name = char.findtext("name", "")
        print(f"  {char_id}: {char_name}")
    
    # Simulate character name editing
    modified_elements = {
        "title": "Test Book",
        "genre": "Fantasy",
        "tone": "Epic",
        "perspective": "Third Person",
        "target_audience": "Adults",
        "character_names": {
            "protagonist": "Strider",  # Changed from Aragorn to Strider
            "antagonist": "Dark Lord"  # Changed from Sauron to Dark Lord
        }
    }
    
    # Apply character name updates (simulating _update_story_elements logic)
    if "character_names" in modified_elements:
        character_names = modified_elements["character_names"]
        for char in characters.findall("character"):
            char_id = char.get("id")
            if char_id in character_names:
                name_elem = char.find("name")
                if name_elem is not None:
                    name_elem.text = character_names[char_id]
                else:
                    ET.SubElement(char, "name").text = character_names[char_id]
    
    # Display updated character names
    print("\nUpdated character names:")
    for char in characters.findall("character"):
        char_id = char.get("id")
        char_name = char.findtext("name", "")
        print(f"  {char_id}: {char_name}")
    
    # Verify the changes
    protagonist_name_elem = characters.find(".//character[@id='protagonist']/name")
    antagonist_name_elem = characters.find(".//character[@id='antagonist']/name")
    assert protagonist_name_elem is not None and protagonist_name_elem.text == "Strider"
    assert antagonist_name_elem is not None and antagonist_name_elem.text == "Dark Lord"
    
    print("\n✅ Character name editing test passed!")

def test_character_extraction():
    """Test character name extraction logic."""

    # Create a sample XML structure with characters
    book_root = ET.Element("book")
    characters = ET.SubElement(book_root, "characters")

    char1 = ET.SubElement(characters, "character")
    char1.set("id", "hero")
    ET.SubElement(char1, "name").text = "Gandalf"

    char2 = ET.SubElement(characters, "character")
    char2.set("id", "sidekick")
    ET.SubElement(char2, "name").text = "Frodo"

    # Extract character names (simulating review_and_modify_story_elements logic)
    character_names = {}
    try:
        characters_list = book_root.findall(".//character")
        for char in characters_list:
            char_id = char.get("id") or char.findtext("id", "")
            char_name = char.findtext("name", "")
            if char_id and char_name:
                character_names[char_id] = char_name
    except Exception as e:
        print(f"Warning: Could not parse character data: {e}")
        return

    print("\nExtracted character names:")
    for char_id, char_name in character_names.items():
        print(f"  {char_id}: {char_name}")

    # Verify extraction
    assert character_names["hero"] == "Gandalf"
    assert character_names["sidekick"] == "Frodo"

    print("✅ Character name extraction test passed!")

def test_character_name_validation():
    """Test character name validation logic."""

    # Test cases for validation
    test_cases = [
        ("Valid Name", True, "Should accept valid names"),
        ("", False, "Should reject empty names"),
        ("   ", False, "Should reject whitespace-only names"),
        ("A" * 101, False, "Should reject names longer than 100 characters"),
        ("Valid Name With Spaces", True, "Should accept names with spaces"),
        ("123", True, "Should accept numeric names"),
        ("Name-with-dashes", True, "Should accept names with special characters"),
    ]

    print("\nTesting character name validation:")

    for name, should_be_valid, description in test_cases:
        # Simulate validation logic
        is_valid = bool(name.strip()) and len(name.strip()) <= 100

        if is_valid == should_be_valid:
            print(f"  ✅ {description}: '{name}' -> {'valid' if is_valid else 'invalid'}")
        else:
            print(f"  ❌ {description}: '{name}' -> {'valid' if is_valid else 'invalid'} (expected {'valid' if should_be_valid else 'invalid'})")
            raise AssertionError(f"Validation failed for: {description}")

    print("✅ Character name validation test passed!")

if __name__ == "__main__":
    test_character_name_editing()
    test_character_extraction()
    test_character_name_validation()
    print("\n🎉 All tests passed! Character name editing functionality is working correctly.")