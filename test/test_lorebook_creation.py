# -*- coding: utf-8 -*-
"""
Test the lorebook creation functionality without requiring API calls.
"""
import json
from pathlib import Path
import sys
sys.path.append('..')

def test_create_lorebook():
    """Test creating a new lorebook structure."""
    
    # Test lorebook data structure
    test_lorebook = {
        "entries": [
            {
                "keys": ["magic", "spells", "arcane"],
                "content": "The magic system is based on elemental manipulation through precise gestures and ancient words.",
                "comment": "Magic System",
                "enable": True,
                "disable": False
            },
            {
                "keys": ["dragon", "Pyraxis", "fire"],
                "content": "Pyraxis the Ancient is a massive red dragon who guards the Crimson Mountains.",
                "comment": "Pyraxis the Dragon",
                "enable": True,
                "disable": False
            }
        ],
        "name": "test_lorebook",
        "description": "Fiction Fabricator Test Lorebook"
    }
    
    # Save test lorebook
    output_path = Path("test/test_new_lorebook.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_lorebook, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created test lorebook: {output_path}")
    print(f"✓ Contains {len(test_lorebook['entries'])} entries")
    
    # Verify it can be loaded
    with open(output_path, 'r', encoding='utf-8') as f:
        loaded = json.load(f)
    
    print(f"✓ Successfully loaded lorebook with {len(loaded['entries'])} entries")
    return True

if __name__ == "__main__":
    test_create_lorebook()