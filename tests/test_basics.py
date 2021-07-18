from unittest import TestCase
from unittest.mock import patch, MagicMock, call


from ruro import base, basics


class ConstantTestCase(TestCase):
    def test_constant_is_entry_type(self) -> None:
        sut = basics.Constant[int](3)
        self.assertIsInstance(sut, base.BaseEntry)
        expected = 3
        actual = sut()
        self.assertEqual(actual, expected)


class IterableConstantTestCase(TestCase):
    def test_iterable_constant(self) -> None:
        sut = basics.IterableConstant[int](range(10))
        self.assertIsInstance(sut, base.BaseIterableEntry)
        expected = list(range(10))
        actual = list(sut())
        self.assertEqual(actual, expected)

    def test_iterable_constant_iter(self) -> None:
        sut = basics.IterableConstant[int](range(10))
        expected = list(range(10))
        actual = list(sut)
        self.assertEqual(actual, expected)

    @patch("ruro.base.BaseZeroArg._before", return_value=None)
    @patch("ruro.base.Base._after", return_value=None)
    @patch("ruro.base.Base._computed", return_value=None)
    @patch("ruro.base.BaseIterable._each", return_value=None)
    def test_iterable_constant_calls_hooks(
        self, each: MagicMock, computed: MagicMock, after: MagicMock, before: MagicMock
    ) -> None:
        value = [0, 1, 2]
        sut = basics.IterableConstant[int](value)
        expected = [0, 1, 2]
        actual = list(sut())
        self.assertEqual(actual, expected)
        before.assert_called_once_with()
        computed.assert_called_once_with(value)
        after.assert_called_once_with(None, None, None)
        each.assert_has_calls([call(0, 0), call(1, 1), call(2, 2)])


class ExecTestCase(TestCase):
    def test_run_is_exit_type(self) -> None:
        sut = basics.Exec[int]()
        self.assertIsInstance(sut, base.BaseExit)
        expected = 3
        actual = sut(3)
        self.assertEqual(actual, expected)


class MapTestCase(TestCase):
    def test_map(self) -> None:
        sut = basics.Map[int, int](lambda d: d + 1)
        self.assertIsInstance(sut, base.BaseIterablePipeline)
        expected = [1, 2, 4]
        actual = list(sut([0, 1, 3]))
        self.assertEqual(actual, expected)


class FilterTestCase(TestCase):
    def test_filter(self) -> None:
        sut = basics.Filter[int](lambda d: d % 2 == 0)
        self.assertIsInstance(sut, base.BaseIterablePipeline)
        expected = [0, 2, 4]
        actual = list(sut([0, 1, 2, 3, 4, 5]))
        self.assertEqual(actual, expected)


class SumTestCase(TestCase):
    def test_sum(self) -> None:
        sut = basics.Sum[int]()
        self.assertIsInstance(sut, base.BasePipeline)
        expected = 10
        actual = sut([0, 1, 2, 3, 4])
        self.assertEqual(actual, expected)

    def test_sum_with_init(self) -> None:
        sut = basics.Sum[list[int]](list[int]())
        expected = [0, 1, 2, -1, -2]
        actual = sut([[0], [1, 2], [-1, -2]])
        self.assertEqual(actual, expected)
