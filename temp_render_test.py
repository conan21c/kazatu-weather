import os
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

# Dummy weather data for rendering
weather_data = [
    {"id": "almaty", "name": "알마티 시내", "max": 24, "min": 12, "desc": "맑음", "icon": "☀️", "info": "해발 800m"},
    {"id": "shymbulak", "name": "침블락", "max": 14, "min": 4, "desc": "가벼운 눈", "icon": "❄️", "info": "해발 2200m"},
    {"id": "assy", "name": "아씨고원", "max": 12, "min": 2, "desc": "소나기", "icon": "🌧️", "info": "해발 2600m"},
    {"id": "kaindy", "name": "카인디 호수", "max": 17, "min": 7, "desc": "구름조금", "icon": "⛅", "info": "해발 2000m"},
    {"id": "kolsay", "name": "콜사이 호수", "max": 18, "min": 8, "desc": "흐림", "icon": "☁️", "info": "해발 1800m"},
    {"id": "charyn", "name": "차른캐년", "max": 28, "min": 15, "desc": "맑음", "icon": "☀️", "info": "해발 600m"},
    {"id": "altyn_emel", "name": "알틴에멜", "max": 26, "min": 14, "desc": "맑음", "icon": "☀️", "info": "해발 1000m"}
]

ai_advice_list = [
    "차른캐년은 직사광선이 강하니 선글라스와 선크림을 챙기세요.",
    "아씨고원은 고도가 높아 기온이 낮으니 두꺼운 외투가 필요합니다."
]

def render_test_image():
    tomorrow = datetime.now() + timedelta(days=1)
    weekdays_eng = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_eng = weekdays_eng[tomorrow.weekday()]
    date_str = tomorrow.strftime("%Y. %m. %d")

    env = FileSystemLoader('templates')
    template = Environment(loader=env).get_template('weather_dashboard.html')
    html_content = template.render(
        locations=weather_data,
        ai_advice_list=ai_advice_list,
        day_eng=day_eng,
        date_str=date_str
    )
    
    with open("temp_render_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    img_path = "actual_weather_render.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1600})
        page.goto("file://" + os.path.abspath("temp_render_test.html"))
        # Wait for fonts and styles to load
        page.wait_for_timeout(2000) 
        page.screenshot(path=img_path, full_page=True)
        browser.close()
        
    print(f"Rendered image saved as: {img_path}")

if __name__ == "__main__":
    render_test_image()
