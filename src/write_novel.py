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
from src.openaiconnection import call_openai_api
from src.prose import (
    print_and_edit_beat,
    rewrite_prose,
    save_chapter_as_markdown,
    write_prose,
)
from src.synopsis import critique_synopsis, generate_synopsis
from src.title import generate_title
from src.database import save_book, create_database_if_not_exists


def system_message_definition():
    """
    Prompts the user to provide a system message for the AI or uses a default message.
    """

    user_input = input(
        "Would you like to provide a system message for prompting the AI? (Y/N): "
    )
    if user_input.lower() == "y":
        message = input("Please enter your system message: ")
    else:
        message = "You will be playing the role of a best-selling author preparing for and then writing another best selling, dark erotica novel. Your writing is highly erotic and yet easily read and accessible to a wide swath of society that may read it. You are an expert at crafting compelling stories, irresistable hooks and engaging characters the audience can easily identify with enough to keep reading. Your writing is sexually explicit and contains numerous sexual scenes that are described in both exciting and descriptive prose that simulates the build up and release of sexual tension during such an act. You must write a 100% unique creative and in a human-like style using contractions, idioms, transitional phrases, interjections, dangling modifiers and colloquialisms and avoiding repetitive phrases and unnatural sentence structures, while still being unique, sexually stimulating and plagiarism free. \n\n\n\n"
    return message


def write_novel():
    """
    Orchestrates the novel-writing process using various functions and the OpenAI API.
    """

    premise = input_premise()
    system_message = system_message_definition()
    genre = select_genre(premise)
    tone = select_tone(premise)
    style = select_style(premise)
    pov = select_pov(premise)
    #    ideas = generate_ideas(genre, tone, style, pov, premise)
    #   chosen_idea = choose_idea(ideas)
    synopsis = generate_synopsis(genre, style, tone, pov, premise)
    updated_synopsis = critique_synopsis(synopsis)
    book_title = generate_title(
        updated_synopsis, genre, style, tone, pov, premise
    )
    print(f"The title of the novel is: {book_title}")
    characters = generate_characters(
        updated_synopsis, genre, style, tone, pov, premise
    )
    chapters = generate_chapters(
        updated_synopsis, genre, tone, style, pov, premise
    )
    for chapter_title, beats in chapters.items():
        chapter_content = ""
        for beat in beats:
            write_prose(
                beat, genre, tone, pov, characters, style, premise
            )
            print_and_edit_beat(chapter_title, beat, "expanded_content")
            rewrite_prose(
                beat, genre, tone, pov, characters, style
            )  # Call the new function
            print_and_edit_beat(chapter_title, beat, "rewritten_content")
            chapter_content += (
                f"\n\n{beat['rewritten_content']}"  # Use the rewritten content
            )
        print(f"Chapter: {chapter_title}\n{chapter_content}")
        save_chapter_as_markdown(chapter_title, chapter_content, book_title)
    book_data = (book_title, genre, tone, style, pov, premise, characters, chapters)
    create_database_if_not_exists(
        "books.db"
    )  # Replace 'books.db' with your database name
    save_book(book_data)


# Run the novel-writing process

write_novel()
