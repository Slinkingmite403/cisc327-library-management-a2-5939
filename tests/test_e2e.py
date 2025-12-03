import pytest
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p

def test_add_book_and_verify(pw):
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(f"{BASE}/add_book")

    page.fill("input[name='title']", "E2E Test Book")
    page.fill("input[name='author']", "Test Author")
    page.fill("input[name='isbn']", "1234567890123")
    page.fill("input[name='total_copies']", "3")

    page.click("button[type='submit']")

    page.goto(f"{BASE}/catalog")
    assert page.locator("td", has_text="E2E Test Book").count() > 0

    browser.close()

def test_borrow_book_flow(pw):
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(f"{BASE}/catalog")

    row = page.locator("tr", has_text="E2E Test Book")

    row.locator("input[name='patron_id']").fill("123456")

    row.locator("button.btn-success").click()

    assert page.locator("text=Successfully borrowed").count() > 0

    browser.close()
