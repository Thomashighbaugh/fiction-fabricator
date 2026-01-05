# -*- coding: utf-8 -*-
"""
anthropic_client.py - Anthropic client implementation for LLMClientInterface.
"""
import os
import getpass
import time
from typing import Optional

import anthropic

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from src import config
from src.llm_client_interface import LLMClientInterface


class AnthropicClient(LLMClientInterface):
    """A client to handle all communication with the Anthropic API."""

    def __init__(self, console: Console):
        self.console = console
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise ValueError("An Anthropic API Key is required.")
        self.client = self._init_client()
        if not self.client:
            raise ConnectionError("Failed to initialize the Anthropic client.")

    def initialize(self) -> bool:
        """Initialize the client (already done in __init__)."""
        return self.client is not None

    def _get_api_key(self) -> str | None:
        """Gets Anthropic API key from environment variables or prompts the user."""
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.console.print("[yellow]ANTHROPIC_API_KEY not found in .env file or environment.[/yellow]")
            try:
                api_key = getpass.getpass("Enter your Anthropic API Key: ")
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[red]Could not read API key from input.[/red]")
                return None
        return api_key

    def _init_client(self) -> anthropic.Anthropic | None:
        """Initializes and returns the Anthropic client."""
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            self.console.print(f"[green]Successfully initialized Anthropic client[/green]")
            return client
        except Exception as e:
            self.console.print("[bold red]Fatal Error: Could not initialize Anthropic client.[/bold red]")
            self.console.print(f"Error details: {e}")
            return None

    def get_response(self, prompt: str, task_description: str = "Generating content", allow_stream: bool = True) -> Optional[str]:
        """
        Sends a prompt to the Anthropic API and returns the response.
        Handles API errors with retries and exponential backoff.
        """
        retries = 0
        while retries < config.MAX_API_RETRIES:
            full_response = ""
            try:
                self.console.print(
                    Panel(f"[yellow]Sending request to Anthropic ({task_description})... (Attempt {retries + 1}/{config.MAX_API_RETRIES})[/yellow]", border_style="dim")
                )
                
                if allow_stream:
                    # Streaming response
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                        task = progress.add_task(description="[cyan]Anthropic is thinking...", total=None)
                        
                        self.console.print(f"[cyan]>>> Anthropic Response ({task_description}):[/cyan]")
                        
                        with self.client.messages.stream(
                            max_tokens=config.ANTHROPIC_MAX_TOKENS,
                            messages=[{"role": "user", "content": prompt}],
                            model=config.ANTHROPIC_MODEL_NAME
                        ) as stream:
                            first_chunk = True
                            for text in stream.text_stream:
                                if first_chunk:
                                    progress.update(task, description="[cyan]Receiving response...")
                                    first_chunk = False
                                
                                print(text, end="", flush=True)
                                full_response += text
                        
                        print()  # Newline after streaming
                else:
                    # Non-streaming response
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                        progress.add_task(description="[cyan]Anthropic is thinking...", total=None)
                        
                        response = self.client.messages.create(
                            max_tokens=config.ANTHROPIC_MAX_TOKENS,
                            messages=[{"role": "user", "content": prompt}],
                            model=config.ANTHROPIC_MODEL_NAME
                        )
                        
                        if response.content:
                            full_response = response.content[0].text
                            self.console.print(f"[cyan]>>> Anthropic Response ({task_description}):[/cyan]")
                            self.console.print(f"[dim]{full_response[:1000]}{'...' if len(full_response) > 1000 else ''}[/dim]")
                        else:
                            self.console.print("[yellow]Response completed but contains no text content.[/yellow]")
                            return None

                self.console.print(Panel("[green]✓ Anthropic response received successfully.[/green]", border_style="dim"))
                return full_response

            except Exception as e:
                self.console.print(f"[bold red]API Error: {type(e).__name__} - {e}[/bold red]")
                
                # Handle specific Anthropic errors
                if "rate limit" in str(e).lower():
                    self.console.print("[yellow]Rate limit exceeded. Waiting before retry...[/yellow]")
                elif "authentication" in str(e).lower():
                    self.console.print("[red]Authentication failed. Please check your API key.[/red]")
                    return None
                elif "context length" in str(e).lower():
                    self.console.print("[yellow]Context length exceeded. Consider shortening your prompt.[/yellow]")

            # Retry logic
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