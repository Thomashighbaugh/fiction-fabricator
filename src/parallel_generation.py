"""
parallel_generation.py - Utilities for parallel content generation with async LLM calls.

Enables concurrent chapter generation to speed up batch operations.
"""

import asyncio
from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.progress import Progress


async def generate_chapters_parallel(
    prompts: list[tuple[str, str]], llm_client: Any, console: Console, max_concurrent: int = 3
) -> list[str | None]:
    """
    Generate multiple chapters in parallel with concurrency limit.

    Args:
        prompts: List of (prompt, task_description) tuples
        llm_client: LLM client with get_response_async method
        console: Rich console for output
        max_concurrent: Maximum concurrent API calls (default: 3)

    Returns:
        List of generated contents (None for failed generations)
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_with_semaphore(prompt: str, task_desc: str) -> str | None:
        async with semaphore:
            try:
                return await llm_client.get_response_async(prompt, task_desc, allow_stream=False)
            except Exception as e:
                console.print(f"[red]Error generating {task_desc}: {e}[/red]")
                return None

    tasks = [generate_with_semaphore(prompt, desc) for prompt, desc in prompts]

    return await asyncio.gather(*tasks)


async def generate_with_progress(
    prompts: list[tuple[str, str]], llm_client: Any, console: Console, max_concurrent: int = 3
) -> list[str | None]:
    """
    Generate multiple chapters in parallel with progress tracking.

    Args:
        prompts: List of (prompt, task_description) tuples
        llm_client: LLM client with get_response_async method
        console: Rich console for output
        max_concurrent: Maximum concurrent API calls

    Returns:
        List of generated contents (None for failed generations)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results: list[str | None] = [None] * len(prompts)

    with Progress(console=console) as progress:
        task_id = progress.add_task("[cyan]Generating chapters...", total=len(prompts))

        async def generate_one(index: int, prompt: str, task_desc: str) -> None:
            async with semaphore:
                try:
                    result = await llm_client.get_response_async(
                        prompt, task_desc, allow_stream=False
                    )
                    results[index] = result
                except Exception as e:
                    console.print(f"[red]Error generating {task_desc}: {e}[/red]")
                    results[index] = None
                finally:
                    progress.update(task_id, advance=1)

        tasks = [generate_one(i, prompt, desc) for i, (prompt, desc) in enumerate(prompts)]

        await asyncio.gather(*tasks)

    return results


def run_parallel_generation(
    prompts: list[tuple[str, str]],
    llm_client: Any,
    console: Console,
    max_concurrent: int = 3,
    show_progress: bool = True,
) -> list[str | None]:
    """
    Synchronous wrapper for parallel chapter generation.

    Use this from synchronous code (like orchestrator).

    Args:
        prompts: List of (prompt, task_description) tuples
        llm_client: LLM client with get_response_async method
        console: Rich console for output
        max_concurrent: Maximum concurrent API calls
        show_progress: Whether to show progress bar

    Returns:
        List of generated contents

    Example:
        prompts = [
            (prompt1, "Chapter 1"),
            (prompt2, "Chapter 2"),
            (prompt3, "Chapter 3"),
        ]
        results = run_parallel_generation(prompts, llm_client, console)
    """
    if show_progress:
        coro = generate_with_progress(prompts, llm_client, console, max_concurrent)
    else:
        coro = generate_chapters_parallel(prompts, llm_client, console, max_concurrent)

    return asyncio.run(coro)


async def batch_process_with_callback(
    items: list[Any],
    process_func: Callable[[Any], Any],
    max_concurrent: int = 3,
    on_complete: Callable[[int, Any], None] | None = None,
) -> list[Any]:
    """
    Generic parallel batch processing with optional completion callback.

    Args:
        items: Items to process
        process_func: Async function to process each item
        max_concurrent: Maximum concurrent operations
        on_complete: Optional callback(index, result) after each completion

    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results: list[Any] = [None] * len(items)

    async def process_one(index: int, item: Any) -> None:
        async with semaphore:
            try:
                result = await process_func(item)
                results[index] = result
                if on_complete:
                    on_complete(index, result)
            except Exception:
                results[index] = None
                if on_complete:
                    on_complete(index, None)

    tasks = [process_one(i, item) for i, item in enumerate(items)]
    await asyncio.gather(*tasks)

    return results
