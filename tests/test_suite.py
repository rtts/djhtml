import os
import unittest

from djhtml.modes import DjHTML


class TestSuite(unittest.TestCase):
    maxDiff = None
    DIR = os.path.join(os.path.dirname(__file__), "suite")

    def test_available_files(self):
        """
        Loop over all the files in the suite directory and compare the
        expected output to the actual output.

        """
        for filename in os.listdir(self.DIR):
            with self.subTest(filename):
                self._test_file(filename)

    def _test_file(self, filename):
        with open(os.path.join(self.DIR, filename)) as f:
            expected_output = f.read()

        # Indent the expected output to 0 (no indentation)
        unindented = DjHTML(expected_output).indent(0)
        self.assertNotEqual(unindented, expected_output)

        # Re-indent the unindented output to 4
        actual_output = DjHTML(unindented).indent(4)
        self.assertEqual(expected_output, actual_output)
