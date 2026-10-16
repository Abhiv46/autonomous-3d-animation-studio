from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from platforms.live_production import LiveProductionGate


def test_live_gate_blocks_until_approval_and_files_exist(tmp_path):
    gate = LiveProductionGate(config={"platforms": {"youtube": {"enabled": True}}}, repo_root=str(tmp_path))
    status = gate.inspect()
    assert status["ready"] is False
    assert "LIVE_PUBLISH_APPROVED" in " ".join(status["reasons"]) or status["status"] == "BLOCKED"

    approval_path = tmp_path / "live_publish_approved.txt"
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "token.pickle").write_bytes(b"token")
    (tmp_path / "config" / "client_secret.json").write_text("{}", encoding="utf-8")
    os.environ["LIVE_PUBLISH_APPROVED"] = "true"
    approval = gate.write_approval_file(str(approval_path))
    assert approval["approved"] is True
    status = gate.inspect()
    assert status["status"] == "BLOCKED"


def test_saved_approval_persists_across_processes_but_credentials_are_still_required(
    tmp_path,
    monkeypatch,
):
    monkeypatch.delenv("LIVE_PUBLISH_APPROVED", raising=False)
    for name in (
        "YOUTUBE_TOKEN_PICKLE_PATH",
        "YOUTUBE_CLIENT_SECRET_PATH",
        "LIVE_APPROVAL_FILE",
    ):
        monkeypatch.delenv(name, raising=False)

    gate = LiveProductionGate(
        config={"platforms": {"youtube": {"enabled": True}}},
        repo_root=str(tmp_path),
    )
    gate.write_approval_file()
    status = gate.inspect()

    assert status["ready"] is False
    assert not any(
        "LIVE_PUBLISH_APPROVED" in reason for reason in status["reasons"]
    )
    assert any("credential file" in reason for reason in status["reasons"])


def test_live_gate_uses_tiktok_handle_instead_of_unused_session_file(tmp_path, monkeypatch):
    monkeypatch.delenv("LIVE_PUBLISH_APPROVED", raising=False)
    monkeypatch.delenv("LIVE_APPROVAL_FILE", raising=False)
    config = {
        "platforms": {
            "youtube": {"enabled": True},
            "tiktok": {"enabled": True, "channel_handle": "@thenaughtyduoofficial"},
        }
    }
    gate = LiveProductionGate(config=config, repo_root=str(tmp_path))
    gate.write_approval_file()
    paths = gate.inspect()["paths"]

    assert "tiktok_session" not in paths
    assert "TIKTOK_SESSION_PATH" not in " ".join(gate.inspect()["reasons"])


def test_live_gate_discovers_adjacent_google_oauth_client(tmp_path, monkeypatch):
    monkeypatch.delenv("YOUTUBE_CLIENT_SECRET_PATH", raising=False)
    repo_root = tmp_path / "project"
    (tmp_path / "client_secrets.json").write_text(
        '{"installed": {}}',
        encoding="utf-8",
    )
    gate = LiveProductionGate(repo_root=str(repo_root))

    assert gate.inspect()["paths"]["youtube_client_secret"] == str(
        tmp_path / "client_secrets.json"
    )
