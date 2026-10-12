"""Passing tests for the green fixture. `python -m unittest` exits 0."""
import unittest

from parse import parse_age


class TestParseAge(unittest.TestCase):
    def test_valid(self) -> None:
        self.assertEqual(parse_age(" 42 "), 42)

    def test_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_age("   ")

    def test_non_numeric_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_age("abc")

    def test_out_of_range_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_age("200")


if __name__ == "__main__":
    unittest.main()
