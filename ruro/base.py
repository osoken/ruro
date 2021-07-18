from __future__ import annotations

from abc import ABCMeta, abstractmethod
from types import TracebackType
from typing import TypeVar, Generic, Type, Union, Optional, Literal, overload, cast

from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager


S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")


class BaseCallContext(AbstractContextManager[None], Generic[S, T]):
    def __init__(self, obj: Base[S, T]):
        self._obj = obj

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Literal[False]:
        self._obj._after(exc_type, excinst, exctb)
        return False


class OneArgCallContext(BaseCallContext[S, T]):
    def __init__(self, obj: BaseOneArg[S, T], arg: S):
        super(OneArgCallContext, self).__init__(obj)
        self._arg = arg

    def __enter__(self) -> None:
        cast(BaseOneArg[S, T], self._obj)._before(self._arg)


class ZeroArgCallContext(BaseCallContext[None, T]):
    def __init__(self, obj: BaseZeroArg[T]):
        super(ZeroArgCallContext, self).__init__(obj)

    def __enter__(self) -> None:
        cast(BaseZeroArg[T], self._obj)._before()


class Base(Generic[S, T], metaclass=ABCMeta):
    def _after(
        self,
        exc_type: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> None:
        return None

    def _computed(self, arg: T) -> None:
        return None


class BaseZeroArg(Base[None, T], metaclass=ABCMeta):
    def _before(self) -> None:
        return None

    def __call__(self) -> T:
        with self._exec_context():
            retval = self._exec()
            self._computed(retval)
            return retval

    def _exec_context(self) -> ZeroArgCallContext[T]:
        return ZeroArgCallContext(self)

    @abstractmethod
    def _exec(self) -> T:
        ...


class BaseOneArg(Base[S, T], metaclass=ABCMeta):
    def _before(self, arg: S) -> None:
        return None

    def __call__(self, arg: S) -> T:
        with self._exec_context(arg):
            retval = self._exec(arg)
            self._computed(retval)
            return retval

    def _exec_context(self, arg: S) -> OneArgCallContext[S, T]:
        return OneArgCallContext(self, arg)

    @abstractmethod
    def _exec(self, arg: S) -> T:
        ...


class BaseIterable(Base[S, Iterable[T]]):
    def _each(self, arg: T, index: int) -> None:
        return None


class BaseZeroArgIterable(BaseZeroArg[Iterable[T]], BaseIterable[None, T]):
    def __call__(self) -> Iterable[T]:
        with self._exec_context():
            retval = self._exec()
            self._computed(retval)
            for i, d in enumerate(retval):
                self._each(d, i)
                yield d


class BaseOneArgIterable(BaseOneArg[S, Iterable[T]], BaseIterable[S, T]):
    def __call__(self, arg: S) -> Iterable[T]:
        with self._exec_context(arg):
            retval = self._exec(arg)
            self._computed(retval)
            for i, d in enumerate(retval):
                self._each(d, i)
                yield d


class BaseExit(BaseOneArg[S, T]):
    def _prepend_pipeline(self, pipeline: BasePipeline[U, S]) -> BaseExit[U, T]:
        def _(arg: U) -> T:
            return self(pipeline(arg))

        return Exit[U, T](_)


class Exit(BaseExit[S, T]):
    def __init__(self, func: Callable[[S], T]) -> None:
        self._func = func

    def _exec(self, arg: S) -> T:
        return self._func(arg)


class BasePipeline(BaseOneArg[S, T]):
    def _append_pipeline(self, pipeline: BasePipeline[T, U]) -> BasePipeline[S, U]:
        def _(arg: S) -> U:
            return pipeline(self(arg))

        return Pipeline[S, U](_)

    @overload
    def __or__(self, other: BasePipeline[T, U]) -> BasePipeline[S, U]:
        ...

    @overload
    def __or__(self, other: BaseExit[T, U]) -> BaseExit[S, U]:
        ...

    def __or__(
        self, other: Union[BasePipeline[T, U], BaseExit[T, U]]
    ) -> Union[BasePipeline[S, U], BaseExit[S, U]]:
        if isinstance(other, BasePipeline):
            return self._append_pipeline(other)
        if isinstance(other, BaseExit):
            return other._prepend_pipeline(self)
        raise TypeError(
            f"unsupported operand type(s) for |: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
        )


class Pipeline(BasePipeline[S, T]):
    def __init__(self, func: Callable[[S], T]) -> None:
        self._func = func

    def _exec(self, arg: S) -> T:
        return self._func(arg)


class BaseEntry(BaseZeroArg[T], metaclass=ABCMeta):
    def _append_pipeline(self, pipeline: BasePipeline[T, U]) -> BaseEntry[U]:
        def _() -> U:
            return pipeline(self())

        return Entry[U](_)

    @overload
    def __or__(self, other: BasePipeline[T, U]) -> BaseEntry[U]:
        ...

    @overload
    def __or__(self, other: BaseExit[T, U]) -> U:
        ...

    def __or__(
        self, other: Union[BasePipeline[T, U], BaseExit[T, U]]
    ) -> Union[BaseEntry[U], U]:
        if isinstance(other, BasePipeline):
            return self._append_pipeline(other)
        if isinstance(other, BaseExit):
            return other(self())
        raise TypeError(
            f"unsupported operand type(s) for |: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
        )


class Entry(BaseEntry[T]):
    def __init__(self, func: Callable[[], T]) -> None:
        self._func = func

    def _exec(self) -> T:
        return self._func()


class BaseIterableEntry(BaseZeroArgIterable[T], BaseEntry[Iterable[T]], Iterable[T]):
    def __iter__(self) -> Iterator[T]:
        retval = self()
        if isinstance(retval, Iterator):
            return retval
        return iter(retval)


class BaseIterableExit(BaseOneArgIterable[S, T], BaseExit[S, Iterable[T]]):
    pass


class BaseIterablePipeline(BaseOneArgIterable[S, T], BasePipeline[S, Iterable[T]]):
    pass


class IterableExit(BaseIterableExit[S, T], Exit[S, Iterable[T]]):
    pass


class IterablePipeline(BaseIterablePipeline[S, T], Pipeline[S, Iterable[T]]):
    pass


class IterableEntry(BaseIterableEntry[T], Entry[Iterable[T]]):
    pass
