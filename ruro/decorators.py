from ruro.base import Entry, Pipeline, Exit, S, T

from collections.abc import Callable


def entry(func: Callable[[], T]) -> Entry[T]:
    return Entry[T](func)


def pipeline(func: Callable[[S], T]) -> Pipeline[S, T]:
    return Pipeline[S, T](func)


def exit(func: Callable[[S], T]) -> Exit[S, T]:
    return Exit[S, T](func)
