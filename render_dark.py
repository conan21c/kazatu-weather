import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import datetime

async def render_dark_sample():
    # Mock data for sample
    date_now = datetime.datetime.now()
    date_str = date_now.strftime("%Y. %m. %d")
    day_eng = date_now.strftime("%A").upper()

    locations = [
        {"name": "알마티 시내", "max": 19, "min": 11, "timeline": [
            {"time": "09:00", "icon": "⛅", "temp": 16, "prob": 0},
            {"time": "12:00", "icon": "☁️", "temp": 18, "prob": 0},
            {"time": "15:00", "icon": "☁️", "temp": 19, "prob": 13},
            {"time": "18:00", "icon": "🌧️", "temp": 16, "prob": 45}
        ]},
        {"name": "침블락", "max": 11, "min": 2, "timeline": [
            {"time": "09:00", "icon": "☁️", "temp": 10, "prob": 0},
            {"time": "12:00", "icon": "☁️", "temp": 11, "prob": 0},
            {"time": "15:00", "icon": "☁️", "temp": 10, "prob": 38},
            {"time": "18:00", "icon": "🌧️", "temp": 7, "prob": 78}
        ]},
        {"name": "아씨고원", "max": 14, "min": -1, "timeline": [
            {"time": "09:00", "icon": "☁️", "temp": 10, "prob": 0},
            {"time": "12:00", "icon": "☁️", "temp": 14, "prob": 0},
            {"time": "15:00", "icon": "☁️", "temp": 11, "prob": 26},
            {"time": "18:00", "icon": "🌧️", "temp": 7, "prob": 52}
        ]},
        {"name": "카인디 호수", "max": 17, "min": 6, "timeline": [
            {"time": "09:00", "icon": "⛅", "temp": 15, "prob": 0},
            {"time": "12:00", "icon": "☁️", "temp": 17, "prob": 11},
            {"time": "15:00", "icon": "☁️", "temp": 16, "prob": 30},
            {"time": "18:00", "icon": "🌧️", "temp": 12, "prob": 33}
        ]},
        {"name": "콜사이 호수", "max": 14, "min": 3, "timeline": [
            {"time": "09:00", "icon": "☀️", "temp": 13, "prob": 0},
            {"time": "12:00", "icon": "☁️", "temp": 14, "prob": 10},
            {"time": "15:00", "icon": "☁️", "temp": 13, "prob": 35},
            {"time": "18:00", "icon": "🌧️", "temp": 10, "prob": 60}
        ]},
        {"name": "차른캐년", "max": 24, "min": 10, "timeline": [
            {"time": "09:00", "icon": "☁️", "temp": 20, "prob": 0},
            {"time": "12:00", "icon": "⛅", "temp": 23, "prob": 0},
            {"time": "15:00", "icon": "☁️", "temp": 23, "prob": 0},
            {"time": "18:00", "icon": "☁️", "temp": 19, "prob": 0}
        ]},
        {"name": "알틴에멜", "max": 25, "min": 13, "timeline": [
            {"time": "09:00", "icon": "⛅", "temp": 20, "prob": 0},
            {"time": "12:00", "icon": "⛅", "temp": 24, "prob": 0},
            {"time": "15:00", "icon": "☁️", "temp": 24, "prob": 0},
            {"time": "18:00", "icon": "☁️", "temp": 21, "prob": 0}
        ]}
    ]

    # Jinja2 setup
    env = Environment(loader=FileSystemLoader('/Users/kunhyangkim/Desktop/antigravity/weather/templates'))
    template = env.get_template('weather_dashboard_dark.html')
    html_content = template.render(date_str=date_str, day_eng=day_eng, locations=locations)

    with open('temp_dark.html', 'w') as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1080, "height": 1500})
        await page.goto(f"file://{os.path.abspath('temp_dark.html')}")
        await page.screenshot(path="dark_weather_card.png", full_page=True)
        await browser.close()
    
    os.remove('temp_dark.html')
    print("Dark mode sample generated.")

if __name__ == "__main__":
    asyncio.run(render_dark_sample())
