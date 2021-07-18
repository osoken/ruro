from collections.abc import Callable, Iterable
from typing import Union, cast, overload, Optional

from ruro.base import (
    BaseEntry,
    BaseIterableEntry,
    BasePipeline,
    BaseIterablePipeline,
    BaseExit,
    S,
    T,
)


class Constant(BaseEntry[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def _exec(self) -> T:
        return self._value


class Exec(BaseExit[T, T]):
    def __init__(self) -> None:
        pass

    def _exec(self, arg: T) -> T:
        return arg


class IterableConstant(BaseIterableEntry[T], Constant[Iterable[T]]):
    pass


class Map(BaseIterablePipeline[Iterable[S], T]):
    def __init__(self, func: Callable[[S], T]):
        self._func = func

    def _exec(self, arg: Iterable[S]) -> Iterable[T]:
        return map(self._func, arg)


class Filter(BaseIterablePipeline[Iterable[S], S]):
    def __init__(self, func: Callable[[S], bool]):
        self._func = func

    def _exec(self, arg: Iterable[S]) -> Iterable[S]:
        return filter(self._func, arg)


class Sum(BasePipeline[Iterable[S], S]):
    def __init__(self, initial_value: Optional[Union[S, int]] = 0):
        self._initial_value = initial_value

    def _exec(self, arg: Iterable[S]) -> S:
        return cast(S, sum(arg, self._initial_value))
