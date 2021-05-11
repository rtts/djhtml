import os
import unittest

from djhtml.modes import HTML


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
                        inputfile = f.readlines()
                    with open(os.path.join(self.DIR, f"{basename}.out"), "r") as f:
                        expected_output = f.readlines()

                    current_mode = HTML
                    current_level = 0
                    actual_output = []
                    for line in inputfile:
                        mode = current_mode(line.rstrip())
                        actual_output.append(mode.get_line(current_level) + "\n")
                        current_level += mode.nextlevel
                        current_mode = mode.nextmode

                    self.assertEqual(expected_output, actual_output)
