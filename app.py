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

try:
    from vocab import cycle, load
except (ImportError, AttributeError):
    from vocab.vocab import cycle, load
from notifier import notify


def positive_seconds(value):
    """argparse type that rejects intervals which would spin the loop."""
    try:
        seconds = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer number of seconds") from exc
    if seconds <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return seconds


def non_negative_seconds(value):
    try:
        seconds = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer number of seconds") from exc
    if seconds < 0:
        raise argparse.ArgumentTypeError("must not be negative")
    return seconds


def show_round(gen, burst, gap):
    """Show `burst` words, `gap` seconds apart."""
    for index in range(burst):
        if index:
            time.sleep(gap)
        notify(next(gen))


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
        type=positive_seconds,
        default=25,
        metavar="SECONDS",
        help="Seconds between notifications (default: 300)",
    )
    parser.add_argument(
        "--burst",
        type=positive_seconds,
        default=2,
        metavar="N",
        help="Words shown per round (default: 1)",
    )
    parser.add_argument(
        "--burst-gap",
        type=non_negative_seconds,
        default=5,
        metavar="SECONDS",
        help="Seconds between words inside a round (default: 15)",
    )
    args = parser.parse_args()

    words = load(args.file)
    if not words:
        print(f"error: no words loaded from {args.file}", file=sys.stderr)
        sys.exit(1)

    gen = cycle(words)

    if args.dry_run:
        word = next(gen)
        print(f"{word['english']} {word['ipa']} — {word['vietnamese']}")
        return

    show_round(gen, args.burst, args.burst_gap)
    if args.once:
        return

    while True:
        time.sleep(args.interval)
        show_round(gen, args.burst, args.burst_gap)


if __name__ == "__main__":
    main()
