from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from browser.google_flow.flow_driver import GoogleFlowProjectLockedDriver


class FakeEditorLocator:
    def count(self):
        return 1


class FakePage:
    def __init__(self):
        self.url = ""
        self.visited = []

    def get_by_role(self, role, name):
        assert role == "button"
        assert name.search("infolillylooks@gmail.com")
        return FakeEditorLocator()

    def goto(self, url, **kwargs):
        self.visited.append(url)
        self.url = url

    def wait_for_timeout(self, timeout):
        pass

    def locator(self, selector):
        assert ":visible" in selector
        return FakeEditorLocator()

    def evaluate(self, script):
        pass


def test_configured_project_uses_project_id_not_internal_account_slot(tmp_path):
    page = FakePage()
    driver = GoogleFlowProjectLockedDriver(str(tmp_path))

    assert driver.open_configured_project(
        page,
        slot_index=4,
        project_id="c30fd23d-5a03-4081-baeb-fad9cbcc6a99",
        project_name="The Naughty Duo",
        expected_email="infolillylooks@gmail.com",
    )

    assert page.visited == [
        "https://flow.google.com/",
        "https://flow.google.com/project/c30fd23d-5a03-4081-baeb-fad9cbcc6a99"
    ]
