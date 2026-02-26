#!/usr/bin/env python3
"""
Simple demonstration of the character name editing feature in Fiction Fabricator.

This script shows how the enhanced story elements review function works
with character name editing capability.
"""

import xml.etree.ElementTree as ET

def demo_character_editing():
    """Demonstrate the character name editing feature."""

    print("\n" + "="*80)
    print("Fiction Fabricator - Story Elements Review Demo")
    print("="*80)

    # Create a sample project structure
    book_root = ET.Element("book")
    ET.SubElement(book_root, "title").text = "The Fellowship of the Ring"

    # Add story elements
    story_elements = ET.SubElement(book_root, "story_elements")
    ET.SubElement(story_elements, "genre").text = "Fantasy"
    ET.SubElement(story_elements, "tone").text = "Epic"
    ET.SubElement(story_elements, "perspective").text = "Third Person"
    ET.SubElement(story_elements, "target_audience").text = "Adults"

    # Add characters
    characters = ET.SubElement(book_root, "characters")

    char1 = ET.SubElement(characters, "character")
    char1.set("id", "protagonist")
    ET.SubElement(char1, "name").text = "Frodo Baggins"
    ET.SubElement(char1, "description").text = "A young hobbit from the Shire"

    char2 = ET.SubElement(characters, "character")
    char2.set("id", "mentor")
    ET.SubElement(char2, "name").text = "Gandalf the Grey"
    ET.SubElement(char2, "description").text = "A wise wizard"

    char3 = ET.SubElement(characters, "character")
    char3.set("id", "antagonist")
    ET.SubElement(char3, "name").text = "Sauron"
    ET.SubElement(char3, "description").text = "The dark lord"

    # Extract current data (simulating the review function)
    current_title = book_root.findtext("title", "Untitled")
    current_genre = story_elements.findtext("genre", "Not specified")
    current_tone = story_elements.findtext("tone", "Not specified")
    current_perspective = story_elements.findtext("perspective", "Not specified")
    current_target_audience = story_elements.findtext("target_audience", "Not specified")

    # Extract character names
    character_names = {}
    for char in book_root.findall(".//character"):
        char_id = char.get("id") or char.findtext("id", "")
        char_name = char.findtext("name", "")
        if char_id and char_name:
            character_names[char_id] = char_name

    # Display current elements
    print("\nGenerated Story Elements:")
    print("-" * 40)
    print(f"Title: {current_title}")
    print(f"Genre: {current_genre}")
    print(f"Tone: {current_tone}")
    print(f"Perspective: {current_perspective}")
    print(f"Target Audience: {current_target_audience}")

    if character_names:
        print("Character Names:")
        for char_id, char_name in character_names.items():
            print(f"  {char_id}: {char_name}")
    else:
        print("Character Names: No characters found")

    print("\n✓ This demo shows the enhanced story elements review with character name editing!")
    print("In the actual application, users would be prompted to modify these values interactively.")
    print("Character names are now included alongside other story elements for editing.")

    # Show what the editing prompts would look like
    print("\nExample Editing Prompts:")
    print("  Title (current: The Fellowship of the Ring): The Fellowship of the Ring")
    print("  Genre (current: Fantasy): High Fantasy")
    print("  Character protagonist (current: Frodo Baggins): Frodo")
    print("  Character mentor (current: Gandalf the Grey): Gandalf")
    print("  Character antagonist (current: Sauron): The Dark Lord")

    print("\nChanges made:")
    print("  • Genre: Fantasy → High Fantasy")
    print("  • Character protagonist: Frodo Baggins → Frodo")
    print("  • Character mentor: Gandalf the Grey → Gandalf")
    print("  • Character antagonist: Sauron → The Dark Lord")

    print("\n" + "="*80)

if __name__ == "__main__":
    demo_character_editing()