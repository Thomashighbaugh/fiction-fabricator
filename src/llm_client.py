"""
llm_client.py - Manages all interactions with the OpenAI API.
"""

import getpass
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from src import config


class LLMClient:
    """A client to handle all communication with the OpenAI API."""

    def __init__(self, console: Console) -> None:
        self.console = console
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise ValueError("An OpenAI API Key is required.")
        self.client = self._init_client()
        if not self.client:
            raise ConnectionError("Failed to initialize the OpenAI client.")

    def _get_api_key(self) -> str | None:
        """Gets NVIDIA API key from environment variables or prompts the user."""
        load_dotenv()
        api_key = os.getenv("NVIDIA_API_KEY")
        if api_key:
            self.console.print("[green]Using NVIDIA_API_KEY from environment.[/green]")
            return api_key

        self.console.print("[yellow]NVIDIA_API_KEY not found in .env file or environment.[/yellow]")
        try:
            api_key = getpass.getpass("Enter your NVIDIA API Key: ")
        except (EOFError, KeyboardInterrupt):
            self.console.print("\n[red]Could not read API key from input.[/red]")
            return None
        return api_key

    def _init_client(self) -> OpenAI | None:
        """Initializes and returns the OpenAI client with NVIDIA endpoint."""
        try:
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=self.api_key)
            self.console.print(
                f"[green]Successfully initialized NVIDIA API client with model '{config.MODEL_NAME}'[/green]"
            )
            return client
        except Exception as e:
            self.console.print(
                "[bold red]Fatal Error: Could not initialize NVIDIA API client.[/bold red]"
            )
            self.console.print(f"Error details: {e}")
            return None

    def get_response(
        self,
        prompt_content: str,
        task_description: str = "Generating content",
        allow_stream: bool = False,
    ) -> str | None:
        """
        Sends a prompt to the LLM and returns the response.
        Handles API errors with retries and exponential backoff.
        """
        retries = 0
        while retries < config.MAX_API_RETRIES:
            full_response = ""
            try:
                self.console.print(
                    Panel(
                        f"[yellow]Sending request to DeepSeek ({task_description})... (Attempt {retries + 1}/{config.MAX_API_RETRIES})[/yellow]",
                        border_style="dim",
                    )
                )

                # --- Non-Streaming Response ---
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[cyan]DeepSeek is thinking...", total=None)

                    response = self.client.chat.completions.create(
                        model=config.MODEL_NAME,
                        messages=[{"role": "user", "content": prompt_content}],
                    )

                    if response.choices[0].message.content:
                        full_response = response.choices[0].message.content
                        self.console.print(
                            f"[cyan]>>> DeepSeek Response ({task_description}):[/cyan]"
                        )
                        self.console.print(
                            f"[dim]{full_response[:1000]}{'...' if len(full_response) > 1000 else ''}[/dim]"
                        )
                    else:
                        self.console.print(
                            "[yellow]Response completed but contains no text content.[/yellow]"
                        )
                        return None

                self.console.print(
                    Panel(
                        "[green]✓ DeepSeek response received successfully.[/green]",
                        border_style="dim",
                    )
                )
                return full_response

            except Exception as e:
                self.console.print(f"[bold red]API Error: {type(e).__name__} - {e}[/bold red]")

                # Handle specific API errors
                if "rate limit" in str(e).lower():
                    self.console.print(
                        "[yellow]Rate limit exceeded. Waiting before retry...[/yellow]"
                    )
                elif "authentication" in str(e).lower():
                    self.console.print(
                        "[red]Authentication failed. Please check your API key.[/red]"
                    )
                    return None
                elif "context length" in str(e).lower():
                    self.console.print(
                        "[yellow]Context length exceeded. Consider shortening your prompt.[/yellow]"
                    )

            # Retry logic
            retries += 1
            if retries < config.MAX_API_RETRIES:
                wait_time = config.API_RETRY_BACKOFF_FACTOR * (2 ** (retries - 1))
                self.console.print(
                    f"[yellow]Waiting {wait_time:.1f} seconds before retrying...[/yellow]"
                )
                time.sleep(wait_time)
                if not Confirm.ask(
                    f"[yellow]Proceed with retry attempt {retries + 1}/{config.MAX_API_RETRIES}? [/yellow]",
                    default=True,
                ):
                    self.console.print("[red]Aborting API call due to user choice.[/red]")
                    return None
            else:
                self.console.print(
                    f"[bold red]Maximum retries ({config.MAX_API_RETRIES}) reached. Failed to get a valid response.[/bold red]"
                )
                return None

        return None
