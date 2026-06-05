"""방안 C 미리보기: 5일 + 인라인 기온 + 폰트 스케일업"""
import os
import urllib.request
import json
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']

LOCATIONS = [
    {"id": "almaty", "name": "알마티 시내", "lat": 43.2389, "lon": 76.8897},
    {"id": "shymbulak", "name": "침블락", "lat": 43.1283, "lon": 77.0805},
    {"id": "assy", "name": "아씨고원", "lat": 43.0858, "lon": 77.8344},
    {"id": "kaindy", "name": "카인디 호수", "lat": 42.9833, "lon": 78.4667},
    {"id": "kolsay", "name": "콜사이 호수", "lat": 42.9469, "lon": 78.3242},
    {"id": "charyn", "name": "차른캐년", "lat": 43.3444, "lon": 79.0833},
    {"id": "altyn_emel", "name": "알틴에멜", "lat": 43.8647, "lon": 78.7461},
]

def get_weather_icon(code):
    weather_codes = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌧️", 53: "🌧️", 55: "🌧️",
        61: "🌧️", 63: "☔", 65: "🌧️",
        71: "🌨️", 73: "❄️", 75: "❄️",
        77: "❄️", 80: "🌧️", 81: "🌧️",
        82: "⛈️", 85: "🌨️", 86: "❄️",
        95: "⛈️", 96: "⛈️", 99: "⛈️",
    }
    return weather_codes.get(code, "🌤️")

def main():
    lats = ",".join([str(loc['lat']) for loc in LOCATIONS])
    lons = ",".join([str(loc['lon']) for loc in LOCATIONS])
    
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lats}&longitude={lons}"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Asia%2FAlmaty"
        f"&forecast_days=8"
    )
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    is_multi = isinstance(data, list)
    
    # 5일: 모레(idx=2)부터 5일
    start_idx = 2
    num_days = 5
    
    results = []
    for i, loc in enumerate(LOCATIONS):
        loc_data = data[i] if is_multi else data
        
        forecast = []
        for d in range(start_idx, start_idx + num_days):
            date_str = loc_data['daily']['time'][d]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            code = loc_data['daily']['weathercode'][d]
            
            forecast.append({
                "date": f"{dt.month}/{dt.day}",
                "day": WEEKDAY_KR[dt.weekday()],
                "icon": get_weather_icon(code),
                "max": round(loc_data['daily']['temperature_2m_max'][d]),
                "min": round(loc_data['daily']['temperature_2m_min'][d]),
                "prob": loc_data['daily']['precipitation_probability_max'][d] or 0,
            })
        
        week_max = max(day["max"] for day in forecast)
        week_min = min(day["min"] for day in forecast)
        
        results.append({
            "name": loc["name"],
            "week_max": week_max,
            "week_min": week_min,
            "forecast": forecast,
        })
    
    # 날짜 범위
    start_date = datetime.now() + timedelta(days=2)
    end_date = start_date + timedelta(days=4)
    date_range = (
        f"{start_date.strftime('%Y. %m. %d')}"
        f"({WEEKDAY_KR[start_date.weekday()]})"
        f" ~ "
        f"{end_date.strftime('%m. %d')}"
        f"({WEEKDAY_KR[end_date.weekday()]})"
    )
    
    ai_advice_list = [
        "주 중반 산악지역 강수확률 높음, 저지대(차른·알틴에멜) 투어 권장",
        "아씨고원·침블락은 비 그친 후 방문 시 맑은 경치 기대, 미끄러운 도로 주의",
        "주말 전 지역 기온 회복, 차른캐년 30°C 이상 고온 예상 — 수분 보충 필수",
    ]
    
    # 렌더링
    env = FileSystemLoader('templates')
    template = Environment(loader=env).get_template('weather_forecast_light_v2.html')
    html_content = template.render(
        date_range=date_range,
        locations=results,
        ai_advice_list=ai_advice_list,
    )
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(base_dir, 'temp_forecast_v2.html')
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    img_path = os.path.join(base_dir, 'forecast_v2_preview.png')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 3000})
        page.goto(f"file://{temp_path}")
        page.wait_for_timeout(1500)
        page.locator('#main-card').screenshot(path=img_path)
        browser.close()
    
    preview_path = os.path.join(base_dir, 'forecast_v2_preview.html')
    os.rename(temp_path, preview_path)
    
    print(f"✅ v2 card: {img_path}")
    print(f"✅ Preview: {preview_path}")

if __name__ == "__main__":
    main()
