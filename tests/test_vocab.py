"""Tests for vocab/vocab.py"""

import io
import sys
import types
import importlib
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Import the module from the sibling vocab/ directory without installing it
# ---------------------------------------------------------------------------
import importlib.util, pathlib

_VOCAB_PATH = pathlib.Path(__file__).parent.parent / "vocab" / "vocab.py"
_spec = importlib.util.spec_from_file_location("vocab", _VOCAB_PATH)
vocab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vocab)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tsv(*rows):
    """Build a TSV string with header + given data rows."""
    lines = ["Tiếng Anh\tTiếng Việt\tPhiên âm IPA"]
    lines.extend("\t".join(r) for r in rows)
    return "\n".join(lines) + "\n"


def _write_tsv(tmp_path, content):
    p = tmp_path / "words.tsv"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# load()
# ---------------------------------------------------------------------------

def test_load_normal(tmp_path):
    p = _write_tsv(tmp_path, _tsv(
        ("hello", "xin chào", "/həˈloʊ/"),
        ("world", "thế giới", "/wɜːrld/"),
    ))
    words = vocab.load(p)
    assert len(words) == 2
    assert words[0] == {"english": "hello", "vietnamese": "xin chào", "ipa": "/həˈloʊ/"}
    assert words[1]["english"] == "world"


def test_load_preserves_special_chars(tmp_path):
    p = _write_tsv(tmp_path, _tsv(
        ("refrigerator (fridge)", "tủ lạnh", "/rɪˈfrɪdʒəreɪtər/ ( /frɪdʒ/ )"),
    ))
    words = vocab.load(p)
    assert words[0]["english"] == "refrigerator (fridge)"
    assert words[0]["ipa"] == "/rɪˈfrɪdʒəreɪtər/ ( /frɪdʒ/ )"


def test_load_skips_blank_lines(tmp_path):
    content = "H\tH\tH\nhello\txin chào\t/həˈloʊ/\n\n\nworld\tthế giới\t/wɜːrld/\n"
    p = _write_tsv(tmp_path, content)
    words = vocab.load(p)
    assert len(words) == 2


def test_load_warns_missing_columns(tmp_path, capsys):
    content = "H\tH\tH\nbad_line\n"
    p = _write_tsv(tmp_path, content)
    words = vocab.load(p)
    assert words == []
    captured = capsys.readouterr()
    assert "warning" in captured.err


def test_load_real_file():
    real = Path(__file__).parent.parent / "vocab" / "tu_vung.txt"
    words = vocab.load(real)
    assert len(words) >= 70   # file has 77 entries
    # Spot-check a known entry
    first = words[0]
    assert first["english"] == "refrigerator (fridge)"
    assert first["ipa"] == "/rɪˈfrɪdʒəreɪtər/ ( /frɪdʒ/ )"


# ---------------------------------------------------------------------------
# cycle()
# ---------------------------------------------------------------------------

def test_cycle_covers_all_words():
    words = [{"english": str(i), "vietnamese": "", "ipa": ""} for i in range(5)]
    seen = set()
    gen = vocab.cycle(words)
    for _ in range(5):
        w = next(gen)
        seen.add(w["english"])
    assert seen == {"0", "1", "2", "3", "4"}


def test_cycle_no_back_to_back_across_rounds():
    random.seed(42)
    words = [{"english": str(i), "vietnamese": "", "ipa": ""} for i in range(4)]
    gen = vocab.cycle(words)
    items = [next(gen) for _ in range(40)]
    for a, b in zip(items, items[1:]):
        assert a is not b, "consecutive items must be different objects"


def test_cycle_single_word():
    w = [{"english": "only", "vietnamese": "", "ipa": ""}]
    gen = vocab.cycle(w)
    for _ in range(5):
        assert next(gen)["english"] == "only"


def test_cycle_empty():
    gen = vocab.cycle([])
    items = list(item for item in (next(gen, None) for _ in range(3)) if item is not None)
    assert items == []
