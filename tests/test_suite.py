import unittest
from pathlib import Path

from djhtml.modes import DjHTML


class TestSuite(unittest.TestCase):
    maxDiff = None
    DIR = Path(__file__).parent / "suite"

    def test_available_files(self) -> None:
        """
        Loop over all the files in the suite directory and compare the
        expected output to the actual output.

        """
        for filename in self.DIR.iterdir():
            if filename.suffix == ".html":
                with self.subTest(filename):
                    self._test_file(filename.stem)

    def _test_file(self, basename: str) -> None:
        with open(self.DIR / (basename + ".html")) as f:
            expected_output = f.read()

        with open(self.DIR / (basename + ".tokens")) as f:
            expected_tokens = f.read()

        # Indent the expected output to 0 (no indentation)
        unindented = DjHTML(
            expected_output, extra_blocks={"weird_tag": "endweird"}
        ).indent(0)
        self.assertNotEqual(unindented, expected_output)

        # Re-indent the unindented output to 4
        actual_output = DjHTML(
            unindented, extra_blocks={"weird_tag": "endweird"}
        ).indent(4)
        self.assertEqual(expected_output, actual_output)

        # Compare the tokenization
        actual_tokens = DjHTML(
            actual_output, extra_blocks={"weird_tag": "endweird"}
        ).debug()
        self.assertEqual(expected_tokens, actual_tokens)
