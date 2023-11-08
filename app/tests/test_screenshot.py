# test_screenshot_logic.py
import hashlib

import pytest
from unittest import mock

from app import crawl_and_screenshot
from app.logic.screenshot import (
    add_screenshot_to_db,
    calculate_checksum,
    take_screenshot,
)


@pytest.fixture
def mock_db_session():
    """Fixture to mock a database session."""

    class MockSession:
        def add(self, obj):
            pass

        def commit(self):
            pass

    return MockSession()


@pytest.fixture
def mock_playwright():
    """Fixture to mock the playwright browser context."""

    class MockBrowser:
        def new_page(self):
            return MockPage()

    class MockPage:
        def goto(self, url):
            pass

        def screenshot(self, path):
            pass

        def close(self):
            pass

        def evaluate(self, script):
            return ["http://example.com"]

    class MockPlaywright:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        @property
        def chromium(self):
            return MockBrowser()

    return MockPlaywright()


def test_calculate_checksum():
    """Test that the checksum is calculated correctly."""
    mock_file_contents = b"file contents"
    expected_checksum = hashlib.sha256(mock_file_contents).hexdigest()
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_file_contents)):
        checksum = calculate_checksum("dummy_path")
    assert checksum == expected_checksum


def test_add_screenshot_to_db(mock_db_session):
    """Test adding a screenshot to the database."""
    with mock.patch("app.logic.screenshot.calculate_checksum", return_value="checksum"):
        new_screenshot = add_screenshot_to_db(
            "unique_id", "path/to/image.png", "image.png", mock_db_session
        )
        assert new_screenshot.checksum == "checksum"


def test_take_screenshot(mock_playwright):
    """Test taking a screenshot with a web page."""
    path = take_screenshot(
        mock_playwright.chromium, "http://example.com", "path/to/screenshot.png"
    )
    assert path == "path/to/screenshot.png"


def test_crawl_and_screenshot(mock_db_session, mock_playwright):
    """Test the crawl and screenshot functionality."""
    with mock.patch(
        "app.logic.screenshot.take_screenshot", return_value="path/to/screenshot.png"
    ):
        with mock.patch(
            "app.logic.screenshot.add_screenshot_to_db", return_value=mock.Mock()
        ):
            paths = crawl_and_screenshot(
                "http://example.com", 5, "unique_id", mock_db_session
            )
            assert len(paths) > 0
