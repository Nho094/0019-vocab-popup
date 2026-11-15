"""test_vocab.py – Unit tests for vocabulary loading, cycling, and CLI dry-run."""

import random
import sys
from pathlib import Path
from unittest.mock import patch

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import app
import vocab


def _write_tsv(path, rows, header="Tiếng Anh\tTiếng Việt\tPhiên âm IPA\n"):
    content = header + "\n".join(rows) + "\n"
    path.write_text(content, encoding="utf-8")
    return path


# 1. Đọc định dạng tệp (file format loading)
def test_load_valid_tsv_format(tmp_path):
    tsv_file = _write_tsv(
        tmp_path / "sample.tsv",
        [
            "hello\txin chào\t/həˈloʊ/",
            "world\tthế giới\t/wɜːrld/",
        ],
    )
    words = vocab.load(tsv_file)
    assert len(words) == 2
    assert words[0] == {"english": "hello", "vietnamese": "xin chào", "ipa": "/həˈloʊ/"}
    assert words[1] == {"english": "world", "vietnamese": "thế giới", "ipa": "/wɜːrld/"}


def test_load_skips_blank_lines_and_whitespace(tmp_path):
    tsv_file = tmp_path / "blanks.tsv"
    tsv_file.write_text(
        "\n\nHeader\tHeader\tHeader\n\napple\ttáo\t/ˈæp.əl/\n   \nbanana\tchuối\t/bəˈnæn.ə/\n\n",
        encoding="utf-8",
    )
    words = vocab.load(tsv_file)
    assert len(words) == 2
    assert words[0]["english"] == "apple"
    assert words[1]["english"] == "banana"


# 2. Xử lý dòng lỗi (handling invalid lines)
def test_load_handles_error_lines_and_warns(tmp_path, capsys):
    tsv_file = _write_tsv(
        tmp_path / "corrupt.tsv",
        [
            "only_one_col",
            "col1\tcol2",
            "valid\thợp lệ\t/ˈvæl.ɪd/",
        ],
    )
    words = vocab.load(tsv_file)
    assert len(words) == 1
    assert words[0]["english"] == "valid"

    err = capsys.readouterr().err
    assert "warning: expected 3 columns" in err
    assert "corrupt.tsv:2" in err
    assert "corrupt.tsv:3" in err


# 3. Hành vi xáo trộn không lặp liên tiếp (cycle shuffling without back-to-back repeats)
def test_cycle_shuffles_and_covers_all_words():
    items = [{"english": f"w{i}", "vietnamese": f"v{i}", "ipa": f"i{i}"} for i in range(5)]
    gen = vocab.cycle(items)
    batch = [next(gen)["english"] for _ in range(5)]
    assert set(batch) == {f"w{i}" for i in range(5)}


def test_cycle_no_back_to_back_repeats_across_rounds():
    random.seed(42)
    items = [{"english": f"w{i}", "vietnamese": f"v{i}", "ipa": f"i{i}"} for i in range(4)]
    gen = vocab.cycle(items)
    words = [next(gen) for _ in range(60)]
    for prev_w, next_w in zip(words, words[1:]):
        assert prev_w != next_w
        assert prev_w is not next_w


def test_cycle_edge_cases():
    single = [{"english": "solo", "vietnamese": "đơn", "ipa": "/ˈsoʊloʊ/"}]
    gen_single = vocab.cycle(single)
    assert [next(gen_single)["english"] for _ in range(3)] == ["solo", "solo", "solo"]

    gen_empty = vocab.cycle([])
    assert list(gen_empty) == []


# 4. Chế độ --dry-run
def test_dry_run_mode_prints_word_and_skips_notify(tmp_path, capsys):
    tsv_file = _write_tsv(
        tmp_path / "dry_run.tsv",
        ["practice\tluyện tập\t/ˈpræk.tɪs/"],
    )
    with patch("sys.argv", ["app.py", "--file", str(tsv_file), "--dry-run"]):
        with patch("app.notify") as mock_notify:
            app.main()
            mock_notify.assert_not_called()

    out = capsys.readouterr().out.strip()
    assert out == "practice /ˈpræk.tɪs/ — luyện tập"


# 5. Xác nhận tệp vocab/tu_vung.txt sẵn có chứa tối thiểu 70 mục hợp lệ khi nạp
def test_existing_tu_vung_contains_at_least_70_valid_entries():
    real_file = Path("vocab/tu_vung.txt")
    assert real_file.exists(), "vocab/tu_vung.txt does not exist"

    words = vocab.load(real_file)
    assert len(words) >= 70, f"Expected at least 70 entries, got {len(words)}"
    for item in words:
        assert item.get("english"), "english column must not be empty"
        assert item.get("vietnamese"), "vietnamese column must not be empty"
        assert item.get("ipa"), "ipa column must not be empty"
