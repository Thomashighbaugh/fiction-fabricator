from src.chapters import generate_beats, generate_chapters, customize_beats
from src.characters import generate_characters
from src.config import (
    input_premise,
    select_genre,
    select_pov,
    select_style,
    select_tone,
    edit_config_variables,
)
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
    if choice.lower() == "l":
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
                        # Populate book_data with loaded values
                        book_data = {
                            "title": book_data.title,
                            "genre": book_data.genre,
                            "tone": book_data.tone,
                            "style": book_data.style,
                            "pov": book_data.pov,
                            "premise": book_data.premise,
                            "characters": book_data.characters,
                            "chapters": book_data.chapters,
                        }
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
    genre = select_genre(premise)
    print(f"The genre is: {genre}")
    book_data["genre"] = genre
    tone = select_tone(premise)
    print(f"The tone of the novel is: {tone}")
    book_data["tone"] = tone
    style = select_style(premise)
    print(f"The style of the novel is: {style}")
    book_data["style"] = style

    pov = select_pov(premise)
    book_data["pov"] = pov
    print(f"The perspective of the novel is: {pov}")

    # Allow editing of config variables
    edit_config_variables(book_data)

    synopsis = generate_synopsis(
        book_data["genre"], book_data["style"], book_data["tone"], book_data["pov"], premise
    )
    updated_synopsis = critique_synopsis(synopsis)
    print(f"The synopsis of the novel is: {updated_synopsis}")
    book_data["synopsis"] = updated_synopsis

    book_title = generate_title(
        updated_synopsis,
        book_data["genre"], book_data["style"],
        book_data["tone"],
        book_data["pov"],
        premise,
    )
    print(f"The title of the novel is: {book_title}")
    book_data["title"] = book_title

    characters = generate_characters(
        updated_synopsis,
        book_data["genre"],
        book_data["style"],
        book_data["tone"],
        book_data["pov"],
        premise,
    )
    book_data["characters"] = characters

    chapters = generate_chapters(
        updated_synopsis,
        book_data["genre"],
        book_data["tone"],
        book_data["style"],
        book_data["pov"],
        premise,
    )

    # Allow customization of chapter outlines
    chapters = customize_beats(chapters)

    # Display the generated chapter outline
    print("Generated Chapter Outline:")
    for chapter_num, chapter_data in chapters.items():
        print(f"Chapter {chapter_num}: {chapter_data['title']}")
        print(f"  - {chapter_data['summary']}")

        # Process beats for each chapter
        chapter_content = ""
        chapter_summary = chapter_data["summary"]
        for beat in generate_beats(chapter_summary):
            beat = write_prose(
                beat,
                chapter_summary,
                book_data["genre"],
                book_data["tone"],
                book_data["pov"],
                characters,
                book_data["style"],
                premise,
                updated_synopsis,
            )
            print_and_edit_beat(chapter_data["title"], beat, "expanded_content")
            beat = rewrite_prose(
                beat,
                chapter_summary,
                book_data["genre"],
                book_data["tone"],
                book_data["pov"],
                characters,
                book_data["style"],
                premise,
                updated_synopsis,
            )
            print_and_edit_beat(chapter_data["title"], beat, "rewritten_content")
            chapter_content += f"\n\n{beat['rewritten_content']}"  # Use the rewritten content
        print(f"Chapter: {chapter_data['title']}\n{chapter_content}")
        save_chapter_as_markdown(chapter_data["title"], chapter_content, book_title)

    book_data["chapters"] = chapters

    # Save project data to the database
    save_book(book_data)
