import json

from src.llmconnection import call_g4f_api
from src.prompts import get_beats_prompt, get_chapter_prompt, get_chapter_summary_prompt

# ───────────────────────────────────────────────────────────────── #
def modify_chapter_summaries(chapters_json):
    """
    Allows users to view and modify chapter summaries.

    Loops until user enters 'done' to indicate they are finished.
    For each iteration, user is prompted to enter a chapter number.
    If the number is valid, the corresponding chapter's summary is displayed,
    and the user is given the opportunity to enter a new summary.
    The new summary is saved to the JSON object and the loop continues.
    If the number is invalid, an error message is displayed and the loop continues.

    Returns the modified JSON object.
    """

    while True:
        print("\nChapters:")
        for i, (title, chapter_data) in enumerate(chapters_json.items()):
            print(f"{i+1}. {title}")

        choice = input("\nEnter chapter number to modify, or 'done': ")
        if choice.lower() == "done":
            break

        try:
            chapter_index = int(choice) - 1
            if 0 <= chapter_index < len(chapters_json):
                selected_title = list(chapters_json.keys())[chapter_index]
                current_summary = chapters_json[selected_title]["summary"]
                print(f"\nCurrent summary for '{selected_title}':\n{current_summary}")

                new_summary = input("Enter new summary: ")
                chapters_json[selected_title]["summary"] = new_summary
                print("Summary updated.")
            else:
                print("Invalid chapter number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'done'.")

    return chapters_json
# ───────────────────────────────────────────────────────────────── #
def generate_chapters(synopsis, genre, style, tone, pov, premise):
    """
    Generates chapter outlines and stores them in JSON format.
    """

    prompt = get_chapter_prompt(synopsis, genre, style, tone, pov, premise)
    response = call_g4f_api(prompt)

    # Split the response into chapters
    chapters_text = response.split("Chapter ")

    chapters_json = {}
    for chapter_text in chapters_text:
        if not chapter_text.strip():
            continue

        # Extract chapter number and title
        chapter_lines = chapter_text.strip().split("\n")
        chapter_number, chapter_title = chapter_lines[0].split(":")
        chapter_number = int(chapter_number)  # Convert chapter number to integer

        # Extract chapter summary
        chapter_summary = "\n".join(chapter_lines[1:])

        chapters_json[chapter_number] = {
            "title": chapter_title.strip(),
            "summary": chapter_summary.strip(),
        }

    return chapters_json

# ───────────────────────────────────────────────────────────────── #
def generate_beats(chapter_summary):
    """
    Generates a list of action beats for a given chapter summary.
    """
    prompt = get_beats_prompt(chapter_summary)
    response = call_g4f_api(prompt)

    # Split the response using the "###" delimiter
    beats_text = response.split("###")

    # Parse and clean the beats
    beats = []
    for beat_text in beats_text:
        beat_text = beat_text.strip()
        if beat_text:
            beats.append({"action_point": beat_text})

    return beats

# ───────────────────────────────────────────────────────────────── #
# chapters.py functions (for user interaction)
def reorder_chapters(chapters_json):
    """
    Allows users to reorder chapters.
    """

    chapter_titles = list(chapters_json.keys())
    print("Current chapter order:")
    for i, title in enumerate(chapter_titles, 1):
        print(f"{i}. {title}")

    while True:
        try:
            old_index = int(input("Enter the number of the chapter to move: ")) - 1
            new_index = int(input("Enter the new position for the chapter: ")) - 1
            if 0 <= old_index < len(chapter_titles) and 0 <= new_index < len(chapter_titles):
                chapter_titles.insert(new_index, chapter_titles.pop(old_index))
                print("Chapters reordered.")
                break
            else:
                print("Invalid indices. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers.")

    # Update chapters_json based on the new order
    reordered_chapters_json = {}
    for i, title in enumerate(chapter_titles):
        reordered_chapters_json[title] = chapters_json[title]

    return reordered_chapters_json

# ───────────────────────────────────────────────────────────────── #
def merge_chapters(chapters_json):
    """
    Allows users to merge chapters.
    """

    chapter_titles = list(chapters_json.keys())
    print("Current chapters:")
    for i, title in enumerate(chapter_titles, 1):
        print(f"{i}. {title}")

    while True:
        try:
            chapter1_index = int(input("Enter the number of the first chapter to merge: ")) - 1
            chapter2_index = int(input("Enter the number of the second chapter to merge: ")) - 1
            if 0 <= chapter1_index < len(chapter_titles) and 0 <= chapter2_index < len(chapter_titles):
                chapter1_title = chapter_titles[chapter1_index]
                chapter2_title = chapter_titles[chapter2_index]

                # Merge beats and create a new chapter title
                merged_beats = chapters_json[chapter1_title] + chapters_json[chapter2_title]
                new_chapter_title = input("Enter the title for the merged chapter: ")

                # Update chapters_json
                del chapters_json[chapter1_title]
                del chapters_json[chapter2_title]
                chapters_json[new_chapter_title] = merged_beats

                print("Chapters merged.")
                break
            else:
                print("Invalid indices. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers.")

    return chapters_json

# ───────────────────────────────────────────────────────────────── #
def customize_beats(chapters_json):
    """
    Allows users to add, remove, or modify beats within chapters.
    """

    print("Current chapters:")
    for chapter_num, chapter_data in chapters_json.items():
        print(f"{chapter_num}. {chapter_data['title']}")

    while True:
        try:
            chapter_num = int(input("Enter the number of the chapter to customize beats: "))
            if chapter_num in chapters_json:
                chapter_data = chapters_json[chapter_num]
                chapter_data.setdefault("beats", [])  # Initialize 'beats' if it doesn't exist
                beats = chapter_data["beats"]

                # Generate initial beats based on the chapter summary
                new_beats = generate_beats(chapter_data['summary'])
                beats.extend(new_beats)

                while True:
                    print("\nBeats for this chapter:")
                    for i, beat in enumerate(beats, 1):
                        print(f"{i}. {beat['action_point']}")

                    choice = input("Enter 'add', 'remove', 'modify', 'done', or 'edit': ")
                    if choice.lower() == "done":
                        break
                    elif choice.lower() == "add":
                        new_beat = {"action_point": input("Enter the new action point: ")}
                        beats.append(new_beat)
                    elif choice.lower() == "remove":
                        beat_index = int(input("Enter the number of the beat to remove: ")) - 1
                        if 0 <= beat_index < len(beats):
                            del beats[beat_index]
                        else:
                            print("Invalid beat index. Please try again.")
                    elif choice.lower() == "modify":
                        beat_index = int(input("Enter the number of the beat to modify: ")) - 1
                        if 0 <= beat_index < len(beats):
                            beats[beat_index]["action_point"] = input("Enter the modified action point: ")
                        else:
                            print("Invalid beat index. Please try again.")
                    elif choice.lower() == 'edit':
                        for i, beat in enumerate(beats):
                            print(f"Beat {i+1}: {beat['action_point']}")
                            edit_choice = input("Edit this beat? (y/n): ")
                            if edit_choice.lower() == 'y':
                                new_action_point = input(f"Enter new action point for beat {i+1}: ")
                                beat['action_point'] = new_action_point
                    else:
                        print("Invalid choice. Please try again.")

                chapters_json[chapter_num]["beats"] = beats  # Update beats in chapters_json
                break
            else:
                print("Invalid chapter index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers.")

    return chapters_json
# ───────────────────────────────────────────────────────────────── #
def generate_and_modify_chapter_summaries(chapters_json, synopsis):
    """
    Generates chapter summaries using AI and allows user modifications.

    Args:
        chapters_json (dict): Existing chapter data with titles.
        synopsis (str): The synopsis of the novel.

    Returns:
        dict: Updated chapters_json with summaries and user edits.
    """

    for chapter_num, chapter_data in chapters_json.items():
        title = chapter_data["title"]
        prompt = get_chapter_summary_prompt(title, synopsis)
        summary = call_g4f_api(prompt)

        print(f"\nAI-Generated Summary for Chapter {chapter_num}: {title}\n")
        print(summary)
        choice = input("\nAccept summary (a), edit (e), or regenerate (r)? ")

        if choice.lower() == 'e':
            new_summary = input("Enter your edited summary: ")
            chapters_json[chapter_num]["summary"] = new_summary
        elif choice.lower() == 'r':
            # Regenerate and repeat the process
            new_summary = call_g4f_api(prompt)
            print(f"\nNew AI-Generated Summary:\n{new_summary}")
            choice = input("\nAccept summary (a) or edit (e)? ")
            if choice.lower() == 'e':
                new_summary = input("Enter your edited summary: ")
            chapters_json[chapter_num]["summary"] = new_summary
        else:
            chapters_json[chapter_num]["summary"] = summary

    return chapters_json