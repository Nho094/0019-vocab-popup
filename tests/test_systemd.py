from pathlib import Path


def test_user_timer_runs_single_notification_every_five_minutes():
    root = Path(__file__).resolve().parents[1]
    timer = (root / "systemd" / "vocab-popup.timer").read_text(encoding="utf-8")
    service = (root / "systemd" / "vocab-popup.service").read_text(encoding="utf-8")
    assert "OnUnitActiveSec=5min" in timer
    assert "Type=oneshot" in service
    assert "--once" in service
