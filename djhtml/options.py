"""
Options set by command-line arguments. Usage:

    import options
    print(f"Tabwidth is {options.tabwidth}")

"""

import argparse
import sys

parser = argparse.ArgumentParser(
    description=(
        "DjHTML is a fully automatic template indenter that works with mixed"
        " HTML/CSS/Javascript templates that contain Django or Jinja template"
        " tags. It works similar to other code-formatting tools such as Black and"
        " interoperates nicely with pre-commit. Full documentation can be found at"
        " https://github.com/rtts/djhtml"
    ),
)
parser.add_argument(
    "-c",
    "--check",
    action="store_true",
    help="check indentation without modifying files",
)
parser.add_argument("-q", "--quiet", action="store_true", help="be quiet")
parser.add_argument(
    "-t",
    "--tabwidth",
    metavar="N",
    type=int,
    default=0,
    help="tabwidth (default is to guess)",
)
parser.add_argument(
    "input_filenames",
    metavar="filename",
    nargs="+",
    help="input filenames (either paths or directories)",
)
parser.add_argument("-d", "--debug", action="store_true", help="debug mode")
parser.add_argument("-i", "--in-place", action="store_true", help=argparse.SUPPRESS)

# Parse arguments and assign attributes to self
self = sys.modules[__name__]
args = parser.parse_args(namespace=self)

if self.in_place:
    sys.exit(
        """
You have called DjHTML with the -i or --in-place argument which
has been deprecated as it's now the default. If you have a custom
pre-commit entry for DjHTML, remove the -i argument from it and
everything will continue to work as before.
"""
    )
