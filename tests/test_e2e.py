"""
End-to-End-Test für das Anlegen einer neuen Aufgabe in der TODO-App.

Ultra-minimal - absolut nötigste Code!
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import Page, Browser, expect


# ==================== FIXTURES ====================

@pytest.fixture(scope="session")
def streamlit_server():
    """Startet Streamlit-Server."""
    app_path = Path(__file__).parent.parent / "app.py"
    
    process = subprocess.Popen(
        ["streamlit", "run", str(app_path), "--server.port", "8501",
         "--server.headless", "true", "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    
    # Warte bis bereit
    for _ in range(30):
        try:
            if requests.get("http://localhost:8501", timeout=1).status_code == 200:
                break
        except:
            time.sleep(0.5)
    
    yield "http://localhost:8501"
    process.kill()


@pytest.fixture
def page(streamlit_server: str, browser: Browser):
    """Erstellt Browser-Page."""
    context = browser.new_context()
    page = context.new_page()
    page.goto(streamlit_server)
    page.wait_for_selector('[data-testid="stAppViewContainer"]')
    page.wait_for_timeout(1000)
    yield page
    context.close()


# ==================== TEST ====================

def test_add_task_via_ui(page: Page):
    """E2E-Test: Aufgabe über UI anlegen → sichtbar und gespeichert."""
    
    # Arrange
    expect(page.locator("h1")).to_contain_text("Todo-App")
    expect(page.locator("text=Noch keine Aufgaben").first).to_be_visible()
    
    # Act
    page.locator('input[placeholder*="Folien"]').first.fill("E2E Test-Aufgabe")
    page.get_by_role("button").filter(has_text="Hinzufügen").first.click()
    page.wait_for_timeout(1000)
    
    # Assert
    expect(page.locator("text=E2E Test-Aufgabe").first).to_be_visible()
    expect(page.locator("text=Noch keine Aufgaben")).not_to_be_visible()
    expect(page.locator("text=Erledigt: 0/1").first).to_be_visible()