import os
import subprocess
import tempfile


def split_into_words_w_newline(text):
    lines = text.split("\n")
    split_text = [line.split(None) for line in lines if line]
    return split_text


def remove_last_n_words(text, n):
    split_text = split_into_words_w_newline(text)
    i = 1
    lines_to_slice = 0
    while True:
        line = split_text[-i]
        if line:
            n_words = len(line)
            if n_words < n:
                n -= n_words
                lines_to_slice += 1
            else:
                split_text[-i] = line[:-n]
                break
        i += 1
        if i > len(split_text):
            break
    split_text = split_text[:-lines_to_slice]
    text = "\n".join([" ".join(line) for line in split_text])
    return text.strip()


def keep_last_n_words(text, n):
    split_text = split_into_words_w_newline(text)
    i = 1
    lines_to_slice = 0
    while True:
        line = split_text[-i]
        if line:
            n_words = len(line)
            if n_words < n:
                n -= n_words
                lines_to_slice += 1
            else:
                split_text[i] = line[-n:]
                break
        i += 1
        if i > len(split_text):
            break
    split_text = split_text[-(lines_to_slice + 1):]
    text = "\n".join([" ".join(line) for line in split_text])
    return text.strip()

async def edit_text_with_editor(text, description=""):
    """Opens a text editor (defined by $EDITOR) to edit the given text.

    Args:
        text (str): The text to be edited.
        description (str, optional): A description of what is being edited, for the user. Defaults to "".

    Returns:
        str: The edited text, or None if the editor was not opened or the user cancelled.
    """
    editor = os.environ.get('EDITOR', 'nano')  # Default to 'nano' if $EDITOR is not set

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as temp_file:
         temp_file.write(text)
         temp_file_path = temp_file.name

    try:
         subprocess.run([editor, temp_file_path], check=True)  # Open editor

         with open(temp_file_path, "r") as temp_file:
             edited_text = temp_file.read()
         return edited_text
    except subprocess.CalledProcessError as e:
         print(f"Error running editor: {e}")
         return None
    except FileNotFoundError:
        print(f"Editor '{editor}' not found.")
        return None
    finally:
        os.remove(temp_file_path)  # Clean up temp file