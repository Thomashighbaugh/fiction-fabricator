#!/usr/bin/python3

import json
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def verify_and_complete_content(
    Interface: Interface,
    _Logger: Logger,
    content: str,
    content_type: str,
    expected_purpose: str,
    selected_model: str,
    continuation_prompt_template: str = None,
    max_completion_attempts: int = 3
) -> str:
    """
    Generic function to verify if generated content is complete and continue generation if needed.
    
    Args:
        Interface: The LLM interface wrapper
        _Logger: Logger instance
        content: The generated content to verify
        content_type: Type of content being verified (e.g., "outline", "chapter", "scene", "premise_list")
        expected_purpose: Description of what the content should accomplish
        selected_model: The model to use for verification and continuation
        continuation_prompt_template: Template for continuation prompt (if None, uses default)
        max_completion_attempts: Maximum number of completion attempts
        
    Returns:
        str: The potentially extended content
    """
    
    if not content or not content.strip():
        _Logger.Log(f"Warning: Empty {content_type} provided to completion verification.", 6)
        return content
    
    _Logger.Log(f"Step 3.5: Verifying {content_type} completion...", 2)
    
    # Default continuation prompt template if none provided
    if continuation_prompt_template is None:
        continuation_prompt_template = """The following {content_type} appears to have been cut off mid-generation. Please continue writing from where it left off, maintaining the same style, tone, and format. Do not restart or summarize - simply continue the content seamlessly.

{content_type}: {expected_purpose}

Current content (potentially incomplete):
{content}

Continue writing from where the above content left off:"""
    
    completion_attempts = 0
    current_content = content
    
    while completion_attempts < max_completion_attempts:
        # Verify if content is complete
        verification_prompt = Writer.Prompts.VERIFY_CONTENT_COMPLETION_PROMPT.format(
            content_type=content_type,
            expected_purpose=expected_purpose,
            content=current_content
        )
        
        messages = [Interface.BuildUserQuery(verification_prompt)]
        
        try:
            _, response_json = Interface.SafeGenerateJSON(
                _Logger, messages, selected_model, _RequiredAttribs=["is_complete", "analysis"]
            )
            
            is_complete = response_json.get("is_complete", True)
            analysis = response_json.get("analysis", "No analysis provided")
            
            _Logger.Log(f"Completion analysis: {analysis}", 3)
            
            if is_complete:
                _Logger.Log(f"{content_type.title()} appears to be complete.", 4)
                break
            else:
                _Logger.Log(f"{content_type.title()} appears to be incomplete. Attempting continuation {completion_attempts + 1}/{max_completion_attempts}...", 4)
                
                # Generate continuation
                continuation_prompt = continuation_prompt_template.format(
                    content_type=content_type,
                    expected_purpose=expected_purpose,
                    content=current_content
                )
                
                continuation_messages = [Interface.BuildUserQuery(continuation_prompt)]
                continuation_messages = Interface.SafeGenerateText(
                    _Logger, continuation_messages, selected_model, min_word_count_target=100
                )
                
                continuation_text = Interface.GetLastMessageText(continuation_messages)
                
                if continuation_text and not "[ERROR:" in continuation_text:
                    # Append the continuation
                    current_content = current_content.rstrip() + "\n\n" + continuation_text.strip()
                    _Logger.Log(f"Added continuation to {content_type}. New length: {len(current_content.split())} words.", 4)
                else:
                    _Logger.Log(f"Failed to generate continuation for {content_type}. Stopping completion attempts.", 6)
                    break
                    
        except Exception as e:
            _Logger.Log(f"Error during {content_type} completion verification: {e}. Stopping completion attempts.", 6)
            break
            
        completion_attempts += 1
    
    if completion_attempts >= max_completion_attempts:
        _Logger.Log(f"Reached maximum completion attempts ({max_completion_attempts}) for {content_type}.", 5)
    
    return current_content


def verify_and_complete_outline(
    Interface: Interface,
    _Logger: Logger,
    outline: str,
    outline_type: str,
    selected_model: str
) -> str:
    """
    Specialized function for verifying and completing outlines.
    """
    continuation_prompt = """The following {content_type} appears to have been cut off mid-generation. Please continue writing from where it left off, maintaining the same markdown format, style, and structure. Do not restart or summarize - simply continue the outline seamlessly.

This should be a complete {content_type} that provides a full story structure.

Current outline (potentially incomplete):
{content}

Continue the outline from where it left off:"""
    
    expected_purpose = f"provide a complete {outline_type} with full story structure, plot progression, and character development"
    
    return verify_and_complete_content(
        Interface=Interface,
        _Logger=_Logger,
        content=outline,
        content_type=outline_type,
        expected_purpose=expected_purpose,
        selected_model=selected_model,
        continuation_prompt_template=continuation_prompt,
        max_completion_attempts=3
    )


def verify_and_complete_chapter(
    Interface: Interface,
    _Logger: Logger,
    chapter_text: str,
    chapter_number: int,
    selected_model: str
) -> str:
    """
    Specialized function for verifying and completing chapter content.
    """
    continuation_prompt = """The following chapter appears to have been cut off mid-generation. Please continue writing from where it left off, maintaining the same narrative style, tone, and character voice. Do not restart or summarize - simply continue the story seamlessly.

This should be a complete chapter that provides narrative progression and character development.

Current chapter (potentially incomplete):
{content}

Continue the chapter from where it left off:"""
    
    expected_purpose = f"provide a complete Chapter {chapter_number} with full narrative development, character progression, and satisfying scene resolution"
    
    return verify_and_complete_content(
        Interface=Interface,
        _Logger=_Logger,
        content=chapter_text,
        content_type=f"Chapter {chapter_number}",
        expected_purpose=expected_purpose,
        selected_model=selected_model,
        continuation_prompt_template=continuation_prompt,
        max_completion_attempts=3
    )


def verify_and_complete_scene(
    Interface: Interface,
    _Logger: Logger,
    scene_text: str,
    chapter_number: int,
    scene_number: int,
    selected_model: str
) -> str:
    """
    Specialized function for verifying and completing scene content.
    """
    continuation_prompt = """The following scene appears to have been cut off mid-generation. Please continue writing from where it left off, maintaining the same narrative style, tone, and character voice. Do not restart or summarize - simply continue the scene seamlessly.

This should be a complete scene that provides narrative progression and character development.

Current scene (potentially incomplete):
{content}

Continue the scene from where it left off:"""
    
    expected_purpose = f"provide a complete Scene {scene_number} of Chapter {chapter_number} with full narrative development and scene resolution"
    
    return verify_and_complete_content(
        Interface=Interface,
        _Logger=_Logger,
        content=scene_text,
        content_type=f"Chapter {chapter_number} Scene {scene_number}",
        expected_purpose=expected_purpose,
        selected_model=selected_model,
        continuation_prompt_template=continuation_prompt,
        max_completion_attempts=3
    )


def verify_and_complete_premises(
    Interface: Interface,
    _Logger: Logger,
    premises_text: str,
    selected_model: str
) -> str:
    """
    Specialized function for verifying and completing premise lists.
    """
    continuation_prompt = """The following premise list appears to have been cut off mid-generation. Please continue writing from where it left off, maintaining the same format and style. Do not restart or summarize - simply continue adding premises to complete the list.

This should be a complete list of 10 distinct story premises.

Current premise list (potentially incomplete):
{content}

Continue the premise list from where it left off:"""
    
    expected_purpose = "provide exactly 10 complete and distinct story premises"
    
    return verify_and_complete_content(
        Interface=Interface,
        _Logger=_Logger,
        content=premises_text,
        content_type="premise list",
        expected_purpose=expected_purpose,
        selected_model=selected_model,
        continuation_prompt_template=continuation_prompt,
        max_completion_attempts=3
    )


def verify_and_complete_prompt(
    Interface: Interface,
    _Logger: Logger,
    prompt_text: str,
    selected_model: str
) -> str:
    """
    Specialized function for verifying and completing story prompts.
    """
    continuation_prompt = """The following story prompt appears to have been cut off mid-generation. Please continue writing from where it left off, maintaining the same format and style. Do not restart or summarize - simply continue developing the prompt to completion.

This should be a complete story prompt with all necessary elements for story generation.

Current prompt (potentially incomplete):
{content}

Continue the prompt from where it left off:"""
    
    expected_purpose = "provide a complete story prompt with genre, characters, conflict, setting, and thematic elements"
    
    return verify_and_complete_content(
        Interface=Interface,
        _Logger=_Logger,
        content=prompt_text,
        content_type="story prompt",
        expected_purpose=expected_purpose,
        selected_model=selected_model,
        continuation_prompt_template=continuation_prompt,
        max_completion_attempts=3
    )