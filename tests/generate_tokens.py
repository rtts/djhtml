#!/usr/bin/env python3
"""
Generate *.tokens files from *.html files in the suite directory.
"""

from pathlib import Path

from djhtml.modes import DjHTML

DIR = Path(__file__).parent / "suite"

for filename in DIR.iterdir():
    if filename.suffix == ".html":
        with open(DIR / filename) as html:
            with open(DIR / (filename.stem + ".tokens"), "w") as f:
                f.write(
                    DjHTML(html.read(), extra_blocks={"weird_tag": "endweird"}).debug()
                )
