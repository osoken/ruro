from unittest import TestCase
from unittest.mock import patch, MagicMock

from typing import Callable, NoReturn
from ruro import decorators, Entry, Pipeline, Exit


class EntryDecoratorTest(TestCase):
    def test_entry_decorator_makes_function_entry(self) -> None:
        @decorators.entry
        def sut() -> int:
            return 3

        self.assertIsInstance(sut, Entry)
        expected = 3
        actual = sut()

        self.assertEqual(actual, expected)


class PipelineDecoratorTest(TestCase):
    def test_pipeline_decorator_makes_function_pipeline(self) -> None:
        @decorators.pipeline
        def sut(a: int) -> int:
            return a + 1

        self.assertIsInstance(sut, Pipeline)
        expected = 3
        actual = sut(2)

        self.assertEqual(actual, expected)


class ExitDecoratorTest(TestCase):
    def test_exit_decorator_makes_function_exit(self) -> None:
        @decorators.exit
        def sut(a: int) -> int:
            return a + 1

        self.assertIsInstance(sut, Exit)
        expected = 3
        actual = sut(2)

        self.assertEqual(actual, expected)
