"""
async_file_utils.py - Async file I/O utilities using aiofiles.

Provides drop-in replacements for synchronous file operations.
"""
from pathlib import Path

import aiofiles


async def read_text_async(filepath: str | Path, encoding: str = "utf-8") -> str:
    """
    Async read text file.

    Args:
        filepath: Path to file
        encoding: Text encoding (default: utf-8)

    Returns:
        File contents as string
    """
    async with aiofiles.open(filepath, encoding=encoding) as f:
        return await f.read()


async def write_text_async(filepath: str | Path, content: str, encoding: str = "utf-8") -> None:
    """
    Async write text file.

    Args:
        filepath: Path to file
        content: Text content to write
        encoding: Text encoding (default: utf-8)
    """
    async with aiofiles.open(filepath, "w", encoding=encoding) as f:
        await f.write(content)


async def read_bytes_async(filepath: str | Path) -> bytes:
    """
    Async read binary file.

    Args:
        filepath: Path to file

    Returns:
        File contents as bytes
    """
    async with aiofiles.open(filepath, "rb") as f:
        return await f.read()


async def write_bytes_async(filepath: str | Path, content: bytes) -> None:
    """
    Async write binary file.

    Args:
        filepath: Path to file
        content: Binary content to write
    """
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)


async def append_text_async(filepath: str | Path, content: str, encoding: str = "utf-8") -> None:
    """
    Async append to text file.

    Args:
        filepath: Path to file
        content: Text content to append
        encoding: Text encoding (default: utf-8)
    """
    async with aiofiles.open(filepath, "a", encoding=encoding) as f:
        await f.write(content)


async def read_lines_async(filepath: str | Path, encoding: str = "utf-8") -> list[str]:
    """
    Async read file lines.

    Args:
        filepath: Path to file
        encoding: Text encoding (default: utf-8)

    Returns:
        List of lines (with newlines preserved)
    """
    async with aiofiles.open(filepath, encoding=encoding) as f:
        return await f.readlines()


async def write_lines_async(
    filepath: str | Path, lines: list[str], encoding: str = "utf-8"
) -> None:
    """
    Async write file lines.

    Args:
        filepath: Path to file
        lines: List of lines to write
        encoding: Text encoding (default: utf-8)
    """
    async with aiofiles.open(filepath, "w", encoding=encoding) as f:
        await f.writelines(lines)


def to_async(filepath: str | Path, mode: str = "r", encoding: str = "utf-8"):
    """
    Context manager for async file operations.

    Usage:
        async with to_async('file.txt', 'r') as f:
            content = await f.read()

    Args:
        filepath: Path to file
        mode: File mode ('r', 'w', 'rb', 'wb', etc.)
        encoding: Text encoding (default: utf-8, ignored for binary modes)

    Returns:
        Async context manager
    """
    if "b" in mode:
        return aiofiles.open(filepath, mode)
    return aiofiles.open(filepath, mode, encoding=encoding)
