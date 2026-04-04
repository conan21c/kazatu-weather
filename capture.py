from playwright.sync_api import sync_playwright
import os

ARTIFACT_PATH = "/Users/kunhyangkim/.gemini/antigravity/brain/ed7adec3-0115-4487-bf9e-284d4295e9a5/artifacts/dashboard_mockup.png"
HTML_PATH = "file://" + os.path.abspath("templates/weather_dashboard.html")

# Create directory if it doesn't exist
os.makedirs(os.path.dirname(ARTIFACT_PATH), exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1080, 'height': 1600})
    page.goto(HTML_PATH)
    page.screenshot(path=ARTIFACT_PATH, full_page=True)
    browser.close()

print(f"Screenshot saved to {ARTIFACT_PATH}")
