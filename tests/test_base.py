from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from collections.abc import Callable, Iterable

from types import TracebackType
from typing import Type, Optional

from ruro import base


class RuroBasicFunctionTestCase(TestCase):
    def test_ruro_objects_can_concat_with_pipe(self) -> None:
        entry_ = base.Entry[int](int)
        pipeline_ = base.Pipeline[int, str](lambda x: str(x))
        exit_ = base.Exit[str, int](lambda x: len(x))
        expected = 1
        actual = entry_ | pipeline_ | exit_
        self.assertEqual(actual, expected)


class RuroAssertionPolicyTestCase(TestCase):
    def test_entry_object_raises_exception_by_default(self) -> None:
        class Example(base.BaseEntry[int]):
            def _exec(self) -> int:
                raise ValueError("string")

        sut = Example()

        with self.assertRaisesRegex(ValueError, "string"):
            _ = sut()

    def test_after_overrides_exception(self) -> None:
        class Example(base.BaseEntry[int]):
            def _exec(self) -> int:
                raise ValueError("string")

            def _after(
                self,
                exc_type: Optional[Type[BaseException]],
                excinst: Optional[BaseException],
                exctb: Optional[TracebackType],
            ) -> None:
                raise TypeError("overridden")

        sut = Example()
        with self.assertRaisesRegex(TypeError, "overridden"):
            _ = sut()

    def test_exception_from_before_not_passed_to_after(self) -> None:
        class Example(base.BaseEntry[int]):
            def _exec(self) -> int:
                return 123

            def _before(self) -> None:
                raise ValueError("raised by before")

            def _after(
                self,
                exc_type: Optional[Type[BaseException]],
                excinst: Optional[BaseException],
                exctb: Optional[TracebackType],
            ) -> None:
                raise TypeError("overridden")

        sut = Example()
        with self.assertRaisesRegex(ValueError, "raised by before"):
            _ = sut()


class BaseEntryTestCase(TestCase):
    def test_exec_doesnt_require_arg(self) -> None:
        class Example(base.BaseEntry[int]):
            def _exec(self) -> int:
                return 123

        sut = Example()
        expected = 123
        actual = sut()
        self.assertEqual(actual, expected)


class EntryTestCase(TestCase):
    def test_entry_is_a_zero_argument_function(self) -> None:
        sut = base.Entry[int](int)
        expected = 0
        actual = sut()
        self.assertEqual(actual, expected)

    def test_entry_calls_hooks(self) -> None:
        sut = base.Entry[int](int)
        expected = 0
        actual = sut()
        self.assertEqual(actual, expected)

    def test_entry_is_a_callable(self) -> None:
        sut = base.Entry[int](lambda: 3)
        self.assertTrue(callable(sut))
        expected = 3
        actual = sut()
        self.assertEqual(actual, expected)

    def test_entry_can_concatenate_to_pipeline_and_returns_entry(self) -> None:
        e = base.Entry[int](lambda: 3)
        p = base.Pipeline[int, int](lambda x: x + 1)
        sut = e | p
        self.assertIsInstance(sut, base.Entry)
        expected = 4
        actual = sut()
        self.assertEqual(actual, expected)

    def test_entry_can_concatenate_to_exit_and_consumed(self) -> None:
        entry = MagicMock(spec=Callable[[], Iterable[int]], return_value=range(3))

        en = base.Entry[Iterable[int]](entry)
        ex = base.Exit[Iterable[int], str](lambda x: str(sum(x)))
        actual = en | ex
        expected = "3"
        self.assertEqual(actual, expected)
        entry.assert_called_once_with()

    def test_type_error_raised_when_entry_is_connected_to_entry(self) -> None:
        with self.assertRaisesRegex(
            TypeError, r"unsupported operand type\(s\) for |: '.+' and '.+'"
        ):
            _ = base.Entry[int](lambda: 3) | base.Entry[int](lambda: 3)  # type: ignore

    @patch("ruro.base.BaseZeroArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    def test_hooked_entry_calls_hooks(
        self, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        sut = base.Entry[int](lambda: 2)

        expected = 2
        actual = sut()
        self.assertEqual(actual, expected)
        before.assert_called_once_with()
        computed.assert_called_once_with(2)
        after.assert_called_once_with(None, None, None)


class ExitTestCase(TestCase):
    def test_exit_is_a_callable(self) -> None:
        sut = base.Exit[Iterable[int], list[int]](list)
        self.assertTrue(callable(sut))
        expected = list(range(3))
        actual = sut(range(3))
        self.assertEqual(actual, expected)

    def test_type_error_raised_when_exit_is_piped(self) -> None:
        with self.assertRaisesRegex(
            TypeError, r"unsupported operand type\(s\) for |: '.+' and '.+'"
        ):
            _ = base.Exit[int, list[int]](lambda d: list[int](range(d))) | base.Entry[
                int
            ](
                lambda: 3
            )  # type: ignore

        with self.assertRaisesRegex(
            TypeError, r"unsupported operand type\(s\) for |: '.+' and '.+'"
        ):
            _ = base.Exit[int, list[int]](
                lambda d: list[int](range(d))
            ) | base.Pipeline[int, int](
                lambda x: x
            )  # type: ignore

        with self.assertRaisesRegex(
            TypeError, r"unsupported operand type\(s\) for |: '.+' and '.+'"
        ):
            _ = base.Exit[int, list[int]](lambda d: list[int](range(d))) | base.Exit[
                int, list[int]
            ](
                lambda d: list[int](range(d))
            )  # type: ignore

    @patch("ruro.base.BaseOneArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    def test_hooked_exit_calls_hooks(
        self, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        sut = base.Exit[int, list[int]](lambda d: list[int](range(d)))

        expected = [0, 1, 2]
        actual = sut(3)
        self.assertEqual(actual, expected)
        before.assert_called_once_with(3)
        computed.assert_called_once_with([0, 1, 2])
        after.assert_called_once_with(None, None, None)


class PipelineTestCase(TestCase):
    def test_pipeline_is_an_callable(self) -> None:
        sut = base.Pipeline[int, int](lambda x: x + 1)
        self.assertTrue(callable(sut))
        expected = 4
        actual = sut(3)
        self.assertEqual(actual, expected)

    def test_pipeline_can_concatenate_to_pipeline_and_returns_pipeline(self) -> None:
        p1 = base.Pipeline[int, int](lambda x: x + 3)
        p2 = base.Pipeline[int, int](lambda x: x - 2)
        sut = p1 | p2
        self.assertIsInstance(sut, base.Pipeline)
        expected = 5
        actual = sut(4)
        self.assertEqual(actual, expected)

    def test_pipeline_can_concatenate_to_exit_and_returns_exit(self) -> None:
        p = base.Pipeline[int, int](lambda x: x + 1)
        e = base.Exit[int, str](lambda x: str(x))
        sut = p | e
        self.assertIsInstance(sut, base.Exit)
        expected = "4"
        actual = sut(3)
        self.assertEqual(actual, expected)

    def test_type_error_raised_when_pipeline_is_connected_to_entry(self) -> None:
        sut = base.Pipeline[int, int](lambda x: x + 1)
        with self.assertRaisesRegex(
            TypeError, r"unsupported operand type\(s\) for |: '.+' and '.+'"
        ):
            _ = sut | base.Entry[int](lambda: 3)  # type: ignore

    def test_type_error_raised_when_argument_is_not_callable(self) -> None:
        with self.assertRaisesRegex(TypeError, "'int' object is not callable"):
            sut = base.Pipeline[int, int](123)  # type: ignore
            _ = sut(1)

    @patch("ruro.base.BaseOneArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    def test_hooked_pipeline_calls_hooks(
        self, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        sut = base.Pipeline[int, list[int]](lambda d: list[int](range(d)))

        expected = [0, 1, 2]
        actual = sut(3)
        self.assertEqual(actual, expected)
        before.assert_called_once_with(3)
        computed.assert_called_once_with([0, 1, 2])
        after.assert_called_once_with(None, None, None)


class IterableEntryTestCase(TestCase):
    def test_iterable_entry(self) -> None:
        sut = base.IterableEntry[int](lambda: range(10))
        self.assertIsInstance(sut, base.BaseIterableEntry)
        expected = list(range(10))
        actual = list(sut())
        self.assertEqual(actual, expected)

    def test_iterable_entry_iter(self) -> None:
        sut = base.IterableEntry[int](lambda: range(10))
        expected = list(range(10))
        actual = list(sut)
        self.assertEqual(actual, expected)

    @patch("ruro.base.BaseZeroArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    @patch("ruro.base.BaseIterable._each", return_value=None)
    def test_hooked_entry_calls_hooks(
        self, each: MagicMock, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        value = [0, 1, 2]
        sut = base.IterableEntry[int](lambda: value)
        expected = [0, 1, 2]
        actual = list(sut())
        self.assertEqual(actual, expected)
        before.assert_called_once_with()
        computed.assert_called_once_with(value)
        after.assert_called_once_with(None, None, None)
        each.assert_has_calls([call(0, 0), call(1, 1), call(2, 2)])


class IterablePipelineTestCase(TestCase):
    def test_iterable_pipeline(self) -> None:
        def sq(it: Iterable[int]) -> Iterable[int]:
            for d in it:
                yield d * d

        sut = base.IterablePipeline[Iterable[int], int](sq)
        self.assertIsInstance(sut, base.Pipeline)
        expected = [i * i for i in range(10)]
        actual = list(sut(range(10)))
        self.assertEqual(actual, expected)

    @patch("ruro.base.BaseOneArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    @patch("ruro.base.BaseIterable._each", return_value=None)
    def test_iterable_pipeline_calls_hooks(
        self, each: MagicMock, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        sq = MagicMock(spec=Callable[[Iterable[int]], Iterable[int]])
        sq.return_value.__iter__.return_value = iter([0, 1, 4])

        value = [0, 1, 2]
        sut = base.IterablePipeline[Iterable[int], int](sq)
        expected = [0, 1, 4]
        actual = list(sut(value))
        self.assertEqual(actual, expected)
        before.assert_called_once_with(value)
        computed.assert_called_once_with(sq.return_value)
        after.assert_called_once_with(None, None, None)
        each.assert_has_calls([call(0, 0), call(1, 1), call(4, 2)])


class IterableExitTestCase(TestCase):
    def test_iterable_exit(self) -> None:
        def str_iter(it: Iterable[int]) -> Iterable[str]:
            for d in it:
                yield str(d)

        sut = base.IterableExit[Iterable[int], str](str_iter)
        self.assertIsInstance(sut, base.Exit)
        expected = ["0", "1", "2", "3"]
        actual = list(sut(range(4)))
        self.assertEqual(actual, expected)

    @patch("ruro.base.BaseOneArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    @patch("ruro.base.BaseIterable._each", return_value=None)
    def test_iterable_pipeline_calls_hooks(
        self, each: MagicMock, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        str_iter = MagicMock(spec=Callable[[Iterable[int]], Iterable[str]])
        str_iter.return_value.__iter__.return_value = iter(["0", "1", "2", "3"])

        value = [0, 1, 2, 3]
        sut = base.IterableExit[Iterable[int], int](str_iter)
        expected = ["0", "1", "2", "3"]
        actual = list(sut(value))
        self.assertEqual(actual, expected)
        before.assert_called_once_with(value)
        computed.assert_called_once_with(str_iter.return_value)
        after.assert_called_once_with(None, None, None)
        each.assert_has_calls([call("0", 0), call("1", 1), call("2", 2), call("3", 3)])

        x = base.IterableEntry[int](lambda: range(10))
