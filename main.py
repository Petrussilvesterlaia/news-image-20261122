"""Entry point for the news-image-20261122 entry.

Draws the front page of *The Daily Ledger* for Sunday, 22 November 2026
(see draw.py for the page itself) and writes it as entry.png into the
output directory: $MAKEFUN_OUTPUT_DIR when set, else /output.

The drawing is deterministic, so every run writes the same bytes.  If the
drawing code cannot run in this environment at all (no Pillow, no fonts),
the entry falls back to copying the entry.png committed beside this file,
which the same drawing code produced - the bytes are identical either way.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def produce(out_path):
    """Write the front page to out_path, drawing it if at all possible."""
    try:
        import draw

        draw.render(out_path)
        return
    except Exception:
        pass  # fall through to the committed copy below
    committed = os.path.join(HERE, "entry.png")
    if os.path.abspath(committed) != os.path.abspath(out_path):
        shutil.copyfile(committed, out_path)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    produce(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
