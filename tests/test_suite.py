import os
import unittest

from djhtml.modes import DjHTML


class TestSuite(unittest.TestCase):
    DIR = os.path.join(os.path.dirname(__file__), "suite")

    def test_available_files(self):
        """
        Loop over all the files in the suite directory and compare the
        expected output to the actual output.

        """
        for filename in os.listdir(self.DIR):
            if filename.endswith(".in"):
                with self.subTest(filename):
                    basename, _ = os.path.splitext(filename)
                    with open(os.path.join(self.DIR, filename), "r") as f:
                        actual_input = f.read()
                    with open(os.path.join(self.DIR, f"{basename}.out"), "r") as f:
                        expected_output = f.read()
                    actual_output = DjHTML(actual_input).indent(4)

                    self.assertEqual(expected_output, actual_output)
