"""
End-to-End-Test für das Anlegen einer neuen Aufgabe in der TODO-App.

Minimale standalone Version - nur das Nötigste!
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, Browser, expect


# ==================== FIXTURES ====================

@pytest.fixture(scope="session")
def streamlit_server():
    """Startet Streamlit-Server."""
    # Finde app.py
    app_path = Path(__file__).parent.parent / "app.py"
    
    # Starte Server
    process = subprocess.Popen(
        ["streamlit", "run", str(app_path),
         "--server.port", "8501",
         "--server.headless", "true",
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Warte bis bereit
    import requests
    for _ in range(30):  # 15 Sekunden max
        try:
            if requests.get("http://localhost:8501", timeout=1).status_code == 200:
                break
        except:
            pass
        time.sleep(0.5)
    
    yield "http://localhost:8501"
    
    process.kill()


@pytest.fixture
def page(streamlit_server: str, browser: Browser):
    """Erstellt Browser-Page."""
    context = browser.new_context()
    page = context.new_page()
    page.goto(streamlit_server, wait_until="networkidle")
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=15000)
    page.wait_for_timeout(1000)
    
    yield page
    
    context.close()


# ==================== TEST ====================

def test_add_task_via_ui(page: Page):
    """E2E-Test: Aufgabe über UI anlegen → sichtbar und gespeichert."""
    
    # Arrange: App ist geladen
    expect(page.locator("h1")).to_contain_text("Todo-App")
    expect(page.locator("text=Noch keine Aufgaben").first).to_be_visible()
    expect(page.locator("text=Erledigt: 0/0 (0%)").first).to_be_visible()
    
    # Act: Aufgabe anlegen
    task_title = "E2E Test-Aufgabe"
    page.locator('input[placeholder*="Folien"]').first.fill(task_title)
    page.get_by_role("button").filter(has_text="Hinzufügen").first.click()
    page.wait_for_timeout(1000)
    
    # Assert: Aufgabe ist sichtbar
    expect(page.locator(f"text={task_title}").first).to_be_visible()
    expect(page.locator("text=Noch keine Aufgaben")).not_to_be_visible()
    expect(page.locator("text=Erledigt: 0/1 (0%)").first).to_be_visible()
    expect(page.locator('input[placeholder*="Folien"]').first).to_have_value("")