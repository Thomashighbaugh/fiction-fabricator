from src.chapters import generate_chapters
from src.characters import generate_characters
from src.config import (
    input_premise,
    select_genre,
    select_pov,
    select_style,
    select_tone,
)
from src.ideas import choose_idea, generate_ideas
from src.openaiconnection import call_g4f_api
from src.prose import (
    print_and_edit_beat,
    rewrite_prose,
    save_chapter_as_markdown,
    write_prose,
)
from src.synopsis import critique_synopsis, generate_synopsis
from src.title import generate_title
from src.database import save_book, get_saved_projects, load_book, create_database_if_not_exists
from src.premise import generate_premises

def write_novel():
    """
    Orchestrates the novel-writing process using various functions and the OpenAI API.
    """

    # Create database if it doesn't exist
    create_database_if_not_exists("books.db")
    # Prompt for new/load project
    choice = input("New project (n) or load saved project (l)? ")
    if choice.lower() == 'l':
        # Load saved project
        saved_projects = get_saved_projects()
        if saved_projects:
            print("Saved Projects:")
            for project_id, project_title in saved_projects:
                print(f"{project_id}. {project_title}")

            while True:
                try:
                    selected_id = int(input("Enter the ID of the project to load: "))
                    book_data = load_book(selected_id)
                    if book_data:
                        break
                    else:
                        print("Invalid project ID. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        else:
            print("No saved projects found. Starting a new project.")
            book_data = {}
    else:
        # Start new project
        book_data = {}

    generate_premises()
    premise = input_premise()
    book_data["premise"] = premise
    save_book(book_data)
    genre = select_genre(premise)
    book_data["genre"] = genre
    save_book(book_data)
    tone = select_tone(premise)
    book_data["tone"] = tone
    save_book(book_data)
    style = select_style(premise)
    book_data["style"] = style
    save_book(book_data)
    pov = select_pov(premise)
    book_data["pov"] = pov
    save_book(book_data)
    synopsis = generate_synopsis(genre, style, tone, pov, premise)
    updated_synopsis = critique_synopsis(synopsis)
    book_data["synopsis"] = updated_synopsis
    save_book(book_data)
    book_title = generate_title(updated_synopsis, genre, style, tone, pov, premise)
    print(f"The title of the novel is: {book_title}")
    book_data["title"] = book_title
    save_book(book_data)
    characters = generate_characters(updated_synopsis, genre, style, tone, pov, premise)
    book_data["characters"] = characters
    save_book(book_data)
    chapters = generate_chapters(updated_synopsis, genre, tone, style, pov, premise)
    for chapter_title, beats in chapters.items():
        chapter_content = ""
        for beat in beats:
            write_prose(beat, genre, tone, pov, characters, style, premise)
            print_and_edit_beat(chapter_title, beat, "expanded_content")
            rewrite_prose(beat, genre, tone, pov, characters, style)  # Call the new function
            print_and_edit_beat(chapter_title, beat, "rewritten_content")
            chapter_content += f"\n\n{beat['rewritten_content']}"  # Use the rewritten content
        print(f"Chapter: {chapter_title}\n{chapter_content}")
        save_chapter_as_markdown(chapter_title, chapter_content, book_title)
    book_data["chapters"] = chapters

    # Save project data to the database
    save_book(book_data)
