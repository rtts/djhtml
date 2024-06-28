#!/usr/bin/env python
"""
Generate *.tokens files from *.html files in the suite directory.

"""

from pathlib import Path

from djhtml.modes import DjHTML

DIR = Path(__file__).parent / "suite"

for filename in DIR.iterdir():
    if filename.suffix == ".html":
        with open(DIR / filename, encoding="utf8") as html:
            with open(DIR / (filename.stem + ".tokens"), "w", encoding="utf8") as f:
                f.write(DjHTML(html.read()).debug())
