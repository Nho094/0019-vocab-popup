"""notifier.py – fire a desktop notification for one vocabulary word."""

import subprocess
import sys


def notify(word):
    """Call notify-send with the English word + IPA as title, Vietnamese meaning as body."""
    title = f"{word['english']} {word['ipa']}"
    body = word["vietnamese"]
    try:
        result = subprocess.run(
            ["notify-send", title, body],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        print(f"notify-send: không thể gửi thông báo: {exc}", file=sys.stderr)
        return False
    if result.returncode:
        detail = (result.stderr or "").strip() or f"thoát với mã {result.returncode}"
        print(f"notify-send: gửi thông báo thất bại: {detail}", file=sys.stderr)
        return False
    return True
