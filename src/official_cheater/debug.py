"""Centralized bug code."""

_debug = False


def set(enabled: bool) -> None:
    """set debug flag."""
    global _debug
    _debug = enabled


def is_set() -> bool:
    """is debug flag set?"""
    return _debug


def log(*args, **kwargs) -> None:
    """wrapper - print debug-only state when flag set"""
    if _debug:
        print(*args, **kwargs)
