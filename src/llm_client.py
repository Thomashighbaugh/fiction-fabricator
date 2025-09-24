# -*- coding: utf-8 -*-
"""
llm_client.py - Manages all interactions with the Google Gemini API.
"""
import os
import getpass
import time
import google.generativeai as genai
from google.generativeai import types
from google.api_core import exceptions as google_api_exceptions
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from src import config

class LLMClient:
    """A client to handle all communication with the Gemini LLM."""

    def __init__(self, console: Console):
        self.console = console
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise ValueError("A Gemini API Key is required.")
        self.client = self._init_client()
        if not self.client:
            raise ConnectionError("Failed to initialize the Gemini client.")

    def _get_api_key(self) -> str | None:
        """Gets Gemini API key from environment variables or prompts the user."""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.console.print("[yellow]GEMINI_API_KEY not found in .env file or environment.[/yellow]")
            try:
                api_key = getpass.getpass("Enter your Gemini API Key: ")
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[red]Could not read API key from input.[/red]")
                return None
        return api_key

    def _init_client(self) -> genai.GenerativeModel | None:
        """Initializes and returns the Gemini client."""
        try:
            genai.configure(api_key=self.api_key)
            client = genai.GenerativeModel(
                model_name=config.WRITING_MODEL_NAME,
                generation_config=config.WRITING_MODEL_CONFIG,
            )
            self.console.print(f"[green]Successfully initialized Gemini client with model '{config.WRITING_MODEL_NAME}'[/green]")
            return client
        except Exception as e:
            self.console.print("[bold red]Fatal Error: Could not initialize Gemini client.[/bold red]")
            self.console.print(f"Error details: {e}")
            return None

    def get_response(self, prompt_content: str, task_description: str = "Generating content", allow_stream: bool = True) -> str | None:
        """
        Sends a prompt to the LLM and returns the response.
        Handles API errors with retries and exponential backoff.
        """
        retries = 0
        while retries < config.MAX_API_RETRIES:
            full_response = ""
            try:
                self.console.print(
                    Panel(f"[yellow]Sending request to Gemini ({task_description})... (Attempt {retries + 1}/{config.MAX_API_RETRIES})[/yellow]", border_style="dim")
                )
                
                response = None # To hold the final response object
                if allow_stream:
                    # --- Streaming Response ---
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                        task = progress.add_task(description="[cyan]Gemini is thinking...", total=None)
                        response_stream = self.client.generate_content(contents=prompt_content, stream=True)
                        
                        self.console.print(f"[cyan]>>> Gemini Response ({task_description}):[/cyan]")
                        first_chunk = True
                        for chunk in response_stream:
                            if first_chunk:
                                progress.update(task, description="[cyan]Receiving response...")
                                first_chunk = False
                            
                            # Check for blocking reasons in each chunk
                            if hasattr(chunk, 'prompt_feedback') and chunk.prompt_feedback.block_reason:
                                reason = chunk.prompt_feedback.block_reason.name
                                raise types.BlockedPromptException(f"Content generation blocked during streaming. Reason: {reason}")
                            
                            # Check for safety issues in candidates
                            if hasattr(chunk, 'candidates') and chunk.candidates:
                                candidate = chunk.candidates[0]
                                if hasattr(candidate, 'finish_reason'):
                                    finish_reason = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                                    if finish_reason in ['SAFETY', 'RECITATION', 'OTHER']:
                                        raise types.BlockedPromptException(f"Content generation blocked during streaming due to {finish_reason}")
                            
                            if hasattr(chunk, 'text') and chunk.text:
                                print(chunk.text, end="", flush=True)
                                full_response += chunk.text
                        
                        # For streaming responses, we don't need to access _response
                        # The final feedback check will be done below if needed
                    print() # Newline after streaming
                else:
                    # --- Non-Streaming Response ---
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                        progress.add_task(description="[cyan]Gemini is thinking...", total=None)
                        response = self.client.generate_content(contents=prompt_content)
                    
                    # Safely try to access response.text
                    try:
                        if hasattr(response, 'text') and response.text:
                            full_response = response.text
                            self.console.print(f"[cyan]>>> Gemini Response ({task_description}):[/cyan]")
                            self.console.print(f"[dim]{full_response[:1000]}{'...' if len(full_response) > 1000 else ''}[/dim]")
                        else:
                            # No text available, check why
                            self._handle_empty_response(response, task_description)
                    except ValueError as ve:
                        # Handle specific "response.text requires valid Part" error
                        if "response.text" in str(ve) and "valid `Part`" in str(ve):
                            self.console.print(f"[yellow]Response contains no valid content parts. Checking finish reason...[/yellow]")
                            self._handle_empty_response(response, task_description)
                        else:
                            raise ve

                # For streaming responses, final response feedback check is handled per chunk
                # For non-streaming responses, check the response object
                if not allow_stream and response and hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                    reason = response.prompt_feedback.block_reason.name
                    raise types.BlockedPromptException(f"Content generation blocked. Reason: {reason}")

                self.console.print(Panel("[green]✓ Gemini response received successfully.[/green]", border_style="dim"))
                return full_response

            except (types.BlockedPromptException, google_api_exceptions.ResourceExhausted, google_api_exceptions.DeadlineExceeded, google_api_exceptions.GoogleAPICallError, ValueError) as e:
                self.console.print(f"[bold red]API Error: {type(e).__name__} - {e}[/bold red]")
                is_safety_error = isinstance(e, types.BlockedPromptException)
                if is_safety_error:
                    self.console.print("[yellow]Safety errors often require prompt changes, but you can retry.[/yellow]")
                    self.console.print("[yellow]Consider simplifying the content or removing potentially problematic text.[/yellow]")
                    if "OTHER" in str(e):
                        self.console.print("[yellow]Note: 'OTHER' finish reason may indicate content policy issues not caught by standard filters.[/yellow]")
                elif "finish_reason" in str(e).lower():
                    self.console.print("[yellow]The model stopped generation early, likely due to content policies.[/yellow]")

            except Exception as e:
                self.console.print(f"[bold red]An unexpected error occurred: {type(e).__name__} - {e}[/bold red]")
                self.console.print_exception(show_locals=False, word_wrap=True)

            # --- Retry Logic ---
            retries += 1
            if retries < config.MAX_API_RETRIES:
                wait_time = config.API_RETRY_BACKOFF_FACTOR * (2 ** (retries - 1))
                self.console.print(f"[yellow]Waiting {wait_time:.1f} seconds before retrying...[/yellow]")
                time.sleep(wait_time)
                if not Confirm.ask(f"[yellow]Proceed with retry attempt {retries + 1}/{config.MAX_API_RETRIES}? [/yellow]", default=True):
                    self.console.print("[red]Aborting API call due to user choice.[/red]")
                    return None
            else:
                self.console.print(f"[bold red]Maximum retries ({config.MAX_API_RETRIES}) reached. Failed to get a valid response.[/bold red]")
                return None
        
        return None

    def _handle_empty_response(self, response, task_description: str):
        """Handle cases where response exists but contains no accessible text."""
        # Check for various blocking reasons
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason.name if hasattr(response.prompt_feedback.block_reason, 'name') else str(response.prompt_feedback.block_reason)
            raise types.BlockedPromptException(f"Content generation blocked. Reason: {reason}")
        
        # Check candidates for safety blocks or other finish reasons
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                finish_reason = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                
                if finish_reason in ['SAFETY', 'RECITATION']:
                    raise types.BlockedPromptException(f"Content generation blocked due to {finish_reason}")
                elif finish_reason == 'OTHER':
                    # Check safety ratings for more details
                    safety_info = ""
                    if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                        blocked_categories = []
                        for rating in candidate.safety_ratings:
                            if hasattr(rating, 'blocked') and rating.blocked:
                                category = rating.category.name if hasattr(rating.category, 'name') else str(rating.category)
                                blocked_categories.append(category)
                        if blocked_categories:
                            safety_info = f" (blocked categories: {', '.join(blocked_categories)})"
                    raise types.BlockedPromptException(f"Content generation stopped for unspecified reasons{safety_info}")
                elif finish_reason == 'STOP':
                    # Normal completion but no text - this can happen with API issues
                    self.console.print(f"[yellow]Response completed normally but contains no text. This may be an API issue.[/yellow]")
                    raise ValueError(f"Response finished with STOP but contains no accessible text content")
                else:
                    raise ValueError(f"Response finished with reason {finish_reason} but contains no text")
        
        # If we get here, we don't know why there's no text
        raise ValueError("Response object exists but does not contain accessible text content")