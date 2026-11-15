"""app.py – vocab-popup CLI entry point.

Usage examples:
  python app.py --file vocab/tu_vung.txt                  # loop every 5 min
  python app.py --file vocab/tu_vung.txt --once           # one notification then exit
  python app.py --file vocab/tu_vung.txt --dry-run        # print one line, no notify-send
  python app.py --file vocab/tu_vung.txt --interval 60    # loop every 60 s
"""

import argparse
import sys
import time

from vocab.vocab import cycle, load
from notifier import notify


def main():
    parser = argparse.ArgumentParser(
        description="Show vocabulary pop-up notifications from a TSV file."
    )
    parser.add_argument("--file", required=True, help="Path to TSV vocabulary file")
    parser.add_argument("--once", action="store_true", help="Show one word then exit")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print one word to stdout and exit (no notification sent)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        metavar="SECONDS",
        help="Seconds between notifications (default: 300)",
    )
    args = parser.parse_args()

    words = load(args.file)
    if not words:
        print(f"error: no words loaded from {args.file}", file=sys.stderr)
        sys.exit(1)

    gen = cycle(words)
    word = next(gen)

    if args.dry_run:
        print(f"{word['english']} {word['ipa']} — {word['vietnamese']}")
        return

    notify(word)
    if args.once:
        return

    while True:
        time.sleep(args.interval)
        notify(next(gen))


if __name__ == "__main__":
    main()
