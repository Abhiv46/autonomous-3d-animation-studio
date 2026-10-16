from pathlib import Path

from browser.engine.browser_manager import BrowserAutomationEngine


class _FakeContext:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _FakePlaywright:
    def __init__(self):
        self.stopped = False

    def stop(self):
        self.stopped = True


def test_cleanup_does_not_remove_browser_profile_lockfiles(tmp_path: Path):
    lock_file = tmp_path / "SingletonLock"
    lock_file.write_text("active profile lock", encoding="utf-8")

    BrowserAutomationEngine.cleanup_stale_processes(
        browser_name="brave.exe",
        user_data_dir=str(tmp_path),
    )

    assert lock_file.exists()


def test_close_disconnects_without_closing_pinned_browser_context():
    engine = BrowserAutomationEngine()
    context = _FakeContext()
    playwright = _FakePlaywright()
    engine.context = context
    engine.playwright = playwright
    engine._owns_context = False

    engine.close()

    assert context.closed is False
    assert playwright.stopped is True
