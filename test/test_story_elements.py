#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to demonstrate the story elements review workflow.
"""

from rich.console import Console

console = Console()

def test_story_elements_workflow():
    """Demonstrates the story elements review workflow."""
    
    console.print("\n[bold cyan]Story Elements Review Workflow - Documentation[/bold cyan]\n")
    
    console.print("[bold yellow]New Step Added:[/bold yellow] Story Elements Review")
    console.print("Location: Between Outline Generation and Content Generation\n")
    
    console.print("[bold green]Workflow Steps:[/bold green]")
    console.print("1. [dim]Outline Generation[/dim] - Generate book outline with AI")
    console.print("2. [bold cyan]Story Elements Review[/bold cyan] - Review and modify (NEW STEP)")
    console.print("3. [dim]Content Generation[/dim] - Generate chapter content")
    console.print("4. [dim]Editing[/dim] - Edit and refine content\n")
    
    console.print("[bold cyan]What Happens in Story Elements Review:[/bold cyan]\n")
    
    console.print("[yellow]Step 1:[/yellow] Display generated story elements")
    console.print("  A table shows the AI-generated assumptions:")
    console.print("  ┌─────────────────────┬──────────────────────────────────┐")
    console.print("  │ Element             │ Current Value                    │")
    console.print("  ├─────────────────────┼──────────────────────────────────┤")
    console.print("  │ Genre               │ Dark Fantasy                     │")
    console.print("  │ Tone                │ Dark and foreboding              │")
    console.print("  │ Perspective         │ Third person limited             │")
    console.print("  │ Target Audience     │ Adult                            │")
    console.print("  └─────────────────────┴──────────────────────────────────┘\n")
    
    console.print("[yellow]Step 2:[/yellow] Ask user if they want to modify")
    console.print("  'Would you like to modify any of these story elements? (y/N)'")
    console.print("  • If No → Keeps generated elements, proceeds to content generation")
    console.print("  • If Yes → Prompts for each element\n")
    
    console.print("[yellow]Step 3:[/yellow] Collect modifications (if user chose Yes)")
    console.print("  For each element, shows:")
    console.print("  'Genre (current: Dark Fantasy): [Enter to keep, or type new value]'")
    console.print("  'Tone (current: Dark and foreboding): [Enter to keep, or type new value]'")
    console.print("  'Perspective (current: Third person limited): [Enter to keep, or type new value]'")
    console.print("  'Target Audience (current: Adult): [Enter to keep, or type new value]'\n")
    
    console.print("[yellow]Step 4:[/yellow] Display summary of changes")
    console.print("  Shows what was modified:")
    console.print("  [green]Changes made:[/green]")
    console.print("  • Tone: Dark and foreboding → Light and humorous")
    console.print("  • Perspective: Third person limited → First person\n")
    
    console.print("[yellow]Step 5:[/yellow] Save updated elements")
    console.print("  Updates the XML and saves to outline.xml\n")
    
    console.print("[bold cyan]Example User Interactions:[/bold cyan]\n")
    
    console.print("[bold]Scenario 1: User keeps all generated elements[/bold]")
    console.print("  Q: Would you like to modify any of these story elements?")
    console.print("  A: [user presses Enter (No)]")
    console.print("  → [green]Keeping generated story elements as-is.[/green]")
    console.print("  → Proceeds to content generation\n")
    
    console.print("[bold]Scenario 2: User modifies some elements[/bold]")
    console.print("  Q: Would you like to modify any of these story elements?")
    console.print("  A: [user types 'y' and presses Enter]")
    console.print("  Q: Genre (current: Dark Fantasy):")
    console.print("  A: [user presses Enter to keep]")
    console.print("  Q: Tone (current: Dark and foreboding):")
    console.print("  A: [user types 'Satirical and witty']")
    console.print("  Q: Perspective (current: Third person limited):")
    console.print("  A: [user presses Enter to keep]")
    console.print("  Q: Target Audience (current: Adult):")
    console.print("  A: [user types 'Young Adult']")
    console.print("  → Shows changes made")
    console.print("  → [green]Story elements updated and saved.[/green]")
    console.print("  → Proceeds to content generation\n")
    
    console.print("[bold green]Benefits:[/bold green]")
    console.print("  ✓ User has control over story direction")
    console.print("  ✓ Can correct AI assumptions before content generation")
    console.print("  ✓ Simple to skip (just press Enter to keep all)")
    console.print("  ✓ Shows exactly what was changed")
    console.print("  ✓ Changes are saved to project XML\n")
    
    console.print("[bold cyan]Technical Implementation:[/bold cyan]")
    console.print("  • Added review_and_modify_story_elements() in src/ui.py")
    console.print("  • Added _update_story_elements() in src/orchestrator.py")
    console.print("  • Integrated into main workflow between steps 1 and 3")
    console.print("  • Updates story_elements XML node with user modifications")
    console.print("  • Saves changes immediately after modification\n")

if __name__ == "__main__":
    test_story_elements_workflow()
