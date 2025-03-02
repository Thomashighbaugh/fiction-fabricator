# utils/async_utils.py
import asyncio
from typing import Coroutine, Any, Optional


async def timeout_wrapper(
    coro: Coroutine, timeout: Optional[float] = None, default_timeout: float = 60.0
) -> Any:
    """
    Wraps an async coroutine with a timeout.
    """
    try:
        if timeout is None:
            timeout = default_timeout
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise  # Re-raise the TimeoutError to be handled by the caller
