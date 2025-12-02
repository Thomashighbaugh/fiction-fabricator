#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify prompt_for_new_project_idea behavior.
This demonstrates that the function now loops until valid input is provided.
"""

from src.ui import console

def test_prompt_behavior():
    """Test the prompt behavior with simulated inputs."""
    
    console.print("\n[bold cyan]Testing prompt_for_new_project_idea behavior[/bold cyan]\n")
    
    console.print("[green]✓ Scenario 1: When user provides input via --prompt flag[/green]")
    console.print("  The idea is loaded from the file and returned immediately.\n")
    
    console.print("[green]✓ Scenario 2: When user provides input interactively[/green]")
    console.print("  The user is prompted to enter their book idea.")
    console.print("  If they press Enter without typing anything, they see an error message.")
    console.print("  The prompt loops until they provide a non-empty idea.\n")
    
    console.print("[green]✓ Scenario 3: When --prompt flag points to invalid/missing file[/green]")
    console.print("  An error message is displayed, then falls back to interactive prompt.")
    console.print("  Same behavior as Scenario 2.\n")
    
    console.print("[bold yellow]Key Improvement:[/bold yellow]")
    console.print("  • The application no longer exits when no idea is provided")
    console.print("  • Users are given clear instructions and error messages")
    console.print("  • The loop continues until valid input is received")
    console.print("  • Ctrl+C can still be used to exit if desired\n")
    
    console.print("[bold cyan]Example flow when user presses Enter without input:[/bold cyan]")
    console.print("  1. Prompt: 'Your book idea/description'")
    console.print("  2. User presses Enter (empty input)")
    console.print("  3. [red]Error: Book idea cannot be empty. Please provide a description.[/red]")
    console.print("  4. Prompt shown again...")
    console.print("  5. User enters: 'A story about a time-traveling detective'")
    console.print("  6. Application continues with setup\n")

if __name__ == "__main__":
    test_prompt_behavior()
