"""Tests for notifier.py and app.py"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import call, patch

import importlib.util

# ---------------------------------------------------------------------------
# Load modules from project root without installing
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

import notifier  # noqa: E402
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("app", _ROOT / "app.py")
app_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(app_mod)


# ---------------------------------------------------------------------------
# notifier.notify()
# ---------------------------------------------------------------------------

def test_notify_calls_notify_send():
    word = {"english": "hello", "ipa": "/həˈloʊ/", "vietnamese": "xin chào"}
    with patch("notifier.subprocess.run") as mock_run:
        notifier.notify(word)
    mock_run.assert_called_once_with(
        ["notify-send", "hello /həˈloʊ/", "xin chào"],
        check=False,
        capture_output=True,
        text=True,
    )


def test_notify_reports_command_failure_to_stderr(capsys):
    word = {"english": "hello", "ipa": "/həˈloʊ/", "vietnamese": "xin chào"}
    with patch("notifier.subprocess.run", return_value=subprocess.CompletedProcess(
            ["notify-send"], 1, stdout="", stderr="D-Bus unavailable")):
        assert notifier.notify(word) is False
    assert "D-Bus unavailable" in capsys.readouterr().err


def test_notify_reports_missing_notify_send_to_stderr(capsys):
    word = {"english": "hello", "ipa": "", "vietnamese": "xin chào"}
    with patch("notifier.subprocess.run", side_effect=FileNotFoundError("notify-send")):
        assert notifier.notify(word) is False
    assert "notify-send" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# app.py --dry-run
# ---------------------------------------------------------------------------

def _tsv_file(tmp_path):
    p = tmp_path / "words.tsv"
    p.write_text(
        "Tiếng Anh\tTiếng Việt\tPhiên âm IPA\n"
        "hello\txin chào\t/həˈloʊ/\n",
        encoding="utf-8",
    )
    return p


def test_dry_run_prints_one_line(tmp_path, capsys):
    p = _tsv_file(tmp_path)
    with patch("sys.argv", ["app.py", "--file", str(p), "--dry-run"]):
        app_mod.main()
    out = capsys.readouterr().out.strip()
    assert out == "hello /həˈloʊ/ — xin chào"


def test_once_calls_notify_once(tmp_path):
    p = _tsv_file(tmp_path)
    with patch("notifier.subprocess.run") as mock_run, \
         patch("sys.argv", ["app.py", "--file", str(p), "--once"]):
        app_mod.main()
    assert mock_run.call_count == 1


def test_empty_file_exits_nonzero(tmp_path):
    p = tmp_path / "empty.tsv"
    p.write_text("Tiếng Anh\tTiếng Việt\tPhiên âm IPA\n", encoding="utf-8")
    with patch("sys.argv", ["app.py", "--file", str(p)]):
        try:
            app_mod.main()
            assert False, "should have called sys.exit"
        except SystemExit as exc:
            assert exc.code != 0
