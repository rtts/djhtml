import os.path
import unittest

from djhtml.djhtml import djhtml_indent


class SampleTests(unittest.TestCase):
    """Tests set of given examples."""

    def test_samples(self):
        for sample in os.listdir("."):
            if not os.path.isdir(sample):
                continue
            with self.subTest(sample=sample):
                with open(os.path.join(sample, "input.html")) as fp:
                    actual = ''.join(djhtml_indent(fp))
                with open(os.path.join(sample, "expected.html")) as fp:
                    expected = fp.read()
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
