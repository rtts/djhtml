import os
import unittest

from djhtml.modes import DjHTML


class TestSuite(unittest.TestCase):
    maxDiff = None
    DIR = os.path.join(os.path.dirname(__file__), "suite")

    def _test_file(self, basename):
        with open(os.path.join(self.DIR, f"{basename}.in"), "r") as f:
            actual_input = f.read()

        try:
            with open(os.path.join(self.DIR, f"{basename}.out"), "r") as f:
                expected_output = f.read()
        except FileNotFoundError:
            expected_output = None

        try:
            with open(os.path.join(self.DIR, f"{basename}.err"), "r") as f:
                expected_error = f.read().strip()
        except FileNotFoundError:
            expected_error = None

        if expected_output is None and expected_error is None:
            self.fail(f"{basename} has no expected error or output.")

        if expected_output is not None and expected_error is not None:
            self.fail(f"{basename} has both expected error and output.")

        try:
            actual_output = DjHTML(actual_input).indent(4)
            actual_error = None
        except Exception as err:
            actual_error = str(err).strip()
            actual_output = None

        self.assertEqual(actual_output, expected_output)
        self.assertEqual(actual_error, expected_error)

    def test_available_files(self):
        """
        Loop over all the files in the suite directory and compare the
        expected output to the actual output.

        """
        for filename in os.listdir(self.DIR):
            if filename.endswith(".in"):
                basename, _ = os.path.splitext(filename)
                with self.subTest(basename):
                    self._test_file(basename)
