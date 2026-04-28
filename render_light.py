import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import datetime

async def render_light_sample():
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

    ai_advice_list = [
        "내일 알마티 시내는 오후 3시경 약한 비가 예상되니 우산을 준비하세요.",
        "침블락과 아씨고원은 기온이 낮고 바람이 강하니 방한복을 꼭 챙기시기 바랍니다.",
        "전반적으로 흐린 날씨지만 투어 활동에는 큰 지장이 없을 것으로 보입니다."
    ]

    # Jinja2 setup
    env = Environment(loader=FileSystemLoader('/Users/kunhyangkim/Desktop/antigravity/weather/templates'))
    template = env.get_template('weather_dashboard_light.html')
    html_content = template.render(
        date_str=date_str, 
        day_eng=day_eng, 
        locations=locations,
        ai_advice_list=ai_advice_list
    )

    with open('temp_light.html', 'w') as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Adjusted height to accommodate larger fonts without cutting off
        await page.set_viewport_size({"width": 1080, "height": 1800})
        await page.goto(f"file://{os.path.abspath('temp_light.html')}")
        await page.screenshot(path="light_weather_card.png", full_page=True)
        await browser.close()
    
    os.remove('temp_light.html')
    print("Light mode sample generated: light_weather_card.png")

if __name__ == "__main__":
    asyncio.run(render_light_sample())
