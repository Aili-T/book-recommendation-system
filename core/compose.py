from typing import Callable, Any, List
from functools import reduce


def compose(*funcs: Callable) -> Callable:
    """
    Compose multiple functions into a single function.
    """
    if not funcs:
        return lambda x: x

    def composed(*args, **kwargs):
        result = funcs[-1](*args, **kwargs)
        for f in reversed(funcs[:-1]):
            result = f(result)
        return result

    return composed


def pipe(value: Any, *funcs: Callable) -> Any:
    """
    Pipe a value through a series of functions.

    """
    return reduce(lambda acc, f: f(acc), funcs, value)


def identity(x: Any) -> Any:
    """Identity function - returns the input unchanged."""
    return x


def constant(x: Any) -> Callable:
    """Create a function that always returns the same value."""
    return lambda *args, **kwargs: x


def tap(f: Callable) -> Callable:
    """
    Execute a side effect and return the original value.
    Useful for debugging in pipelines.
    """

    def tapped(x):
        f(x)
        return x

    return tapped