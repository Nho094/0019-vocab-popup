"""vocab.py – load and iterate vocabulary from a 3-column TSV file.

Columns (tab-separated): English | Vietnamese | IPA
Row 1 is a header and is skipped.  Blank lines are skipped.
Lines with fewer than 3 columns emit a warning to stderr.

Public API
----------
load(path)   -> list[dict]          # [{english, vietnamese, ipa}, ...]
cycle(words) -> Iterator[dict]      # infinite, shuffled, no back-to-back repeat
"""

import random
import sys
from pathlib import Path


def load(path):
    """Read a tab-separated vocabulary file; return a list of word dicts."""
    words = []
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n\r")
            if lineno == 1 or not line.strip():   # skip header and blank lines
                continue
            cols = line.split("\t")
            if len(cols) < 3:
                print(
                    f"{p.name}:{lineno}: warning: expected 3 columns, got {len(cols)} – skipped",
                    file=sys.stderr,
                )
                continue
            words.append({
                "english": cols[0],
                "vietnamese": cols[1],
                "ipa": cols[2],
            })
    return words


def cycle(words):
    """Yield from words in a shuffled loop, never repeating last word across rounds.

    Algorithm: shuffle each round; if the new round's first word equals the
    previous round's last word, swap the first with a random other position.
    """
    if not words:
        return
    if len(words) == 1:
        while True:
            yield words[0]
        return  # unreachable, satisfies linters

    pool = list(words)
    last = None
    while True:
        random.shuffle(pool)
        # Avoid back-to-back duplicate across rounds
        if pool[0] is last and len(pool) > 1:
            swap = random.randrange(1, len(pool))
            pool[0], pool[swap] = pool[swap], pool[0]
        for word in pool:
            last = word
            yield word


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Preview vocabulary cycling.")
    parser.add_argument("file", help="Path to TSV vocabulary file")
    parser.add_argument("-n", type=int, default=10, help="Number of words to show")
    args = parser.parse_args()

    words = load(args.file)
    print(f"Loaded {len(words)} words from {args.file}\n")
    for i, w in enumerate(cycle(words)):
        if i >= args.n:
            break
        print(f"{i+1:3}. {w['english']}  |  {w['vietnamese']}  |  {w['ipa']}")
