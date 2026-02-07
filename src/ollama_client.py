"""
ollama_client.py - Ollama client implementation for LLMClientInterface.
"""

import time

import ollama
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from src import config
from src.llm_client_interface import LLMClientInterface


class OllamaClient(LLMClientInterface):
    """A client to handle all communication with the Ollama API."""

    def __init__(self, console: Console) -> None:
        self.console = console
        self.client = self._init_client()
        if not self.client:
            raise ConnectionError("Failed to initialize the Ollama client.")

    def initialize(self) -> bool:
        """Initialize the client (already done in __init__)."""
        return self.client is not None

    def _init_client(self) -> ollama.Client | None:
        """Initializes and returns the Ollama client."""
        try:
            # Ollama doesn't require API keys, just a running Ollama server
            client = ollama.Client()

            # Test connection by listing available models
            models = client.list()
            if not models.models:
                self.console.print(
                    "[yellow]No models found in Ollama. Please pull a model first.[/yellow]"
                )
                self.console.print("[yellow]Example: ollama pull llama3.2:3b[/yellow]")
                return None

            self.console.print("[green]Successfully connected to Ollama[/green]")
            self.console.print(
                f"[dim]Available models: {', '.join([m.name for m in models.models])}[/dim]"
            )
            return client
        except Exception as e:
            self.console.print("[bold red]Fatal Error: Could not connect to Ollama.[/bold red]")
            self.console.print(f"Error details: {e}")
            self.console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
            return None

    def get_response(
        self, prompt: str, task_description: str = "Generating content", allow_stream: bool = True
    ) -> str | None:
        """
        Sends a prompt to the Ollama API and returns the response.
        Handles API errors with retries and exponential backoff.
        """
        retries = 0
        while retries < config.MAX_API_RETRIES:
            full_response = ""
            try:
                self.console.print(
                    Panel(
                        f"[yellow]Sending request to Ollama ({task_description})... (Attempt {retries + 1}/{config.MAX_API_RETRIES})[/yellow]",
                        border_style="dim",
                    )
                )

                if allow_stream:
                    # Streaming response
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        transient=True,
                    ) as progress:
                        task = progress.add_task(
                            description="[cyan]Ollama is thinking...", total=None
                        )

                        self.console.print(
                            f"[cyan]>>> Ollama Response ({task_description}):[/cyan]"
                        )

                        stream = self.client.generate(
                            model=config.OLLAMA_MODEL_NAME, prompt=prompt, stream=True
                        )

                        first_chunk = True
                        for chunk in stream:
                            if first_chunk:
                                progress.update(task, description="[cyan]Receiving response...")
                                first_chunk = False

                            if chunk.response:
                                print(chunk.response, end="", flush=True)
                                full_response += chunk.response

                        print()  # Newline after streaming
                else:
                    # Non-streaming response
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        transient=True,
                    ) as progress:
                        progress.add_task(description="[cyan]Ollama is thinking...", total=None)

                        response = self.client.generate(
                            model=config.OLLAMA_MODEL_NAME, prompt=prompt
                        )

                        if response.response:
                            full_response = response.response
                            self.console.print(
                                f"[cyan]>>> Ollama Response ({task_description}):[/cyan]"
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
                        "[green]✓ Ollama response received successfully.[/green]",
                        border_style="dim",
                    )
                )
                return full_response

            except Exception as e:
                self.console.print(f"[bold red]API Error: {type(e).__name__} - {e}[/bold red]")

                # Handle specific Ollama errors
                if "connection" in str(e).lower():
                    self.console.print(
                        "[red]Cannot connect to Ollama server. Make sure Ollama is running.[/red]"
                    )
                    self.console.print("[yellow]Run: ollama serve[/yellow]")
                    return None
                elif "model" in str(e).lower():
                    self.console.print("[red]Model not found. Please pull the model first.[/red]")
                    self.console.print(
                        f"[yellow]Run: ollama pull {config.OLLAMA_MODEL_NAME}[/yellow]"
                    )
                    return None

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
