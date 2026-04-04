import os
import urllib.request
import json
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import requests

# 1. Configuration & Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 2. Location Metadata
LOCATIONS = [
    {"id": "almaty", "name": "알마티 시내", "lat": 43.2389, "lon": 76.8897, "info": "해발 800m"},
    {"id": "charyn", "name": "차른캐년", "lat": 43.3444, "lon": 79.0833, "info": "사막기후"},
    {"id": "kolsay", "name": "콜사이 호수", "lat": 42.9469, "lon": 78.3242, "info": "해발 1800m"},
    {"id": "kaindy", "name": "카인디 호수", "lat": 42.9833, "lon": 78.4667, "info": "해발 2000m"},
    {"id": "altyn_emel", "name": "알틴에멜", "lat": 43.8647, "lon": 78.7461, "info": "일교차 큼"},
    {"id": "assy", "name": "아씨고원", "lat": 43.0858, "lon": 77.8344, "info": "해발 2600m"},
    {"id": "shymbulak", "name": "침블락", "lat": 43.1283, "lon": 77.0805, "info": "해발 2200m"}
]

def get_weather_desc(code):
    weather_codes = {
        0: ("맑음", "☀️"), 1: ("구름 조금", "🌤️"), 2: ("구름 많음", "⛅"), 3: ("흐림", "☁️"),
        45: ("안개", "🌫️"), 48: ("안개", "🌫️"),
        51: ("가벼운 비", "🌧️"), 53: ("비", "🌧️"), 55: ("강한 비", "🌧️"),
        61: ("가벼운 비", "☂️"), 63: ("비", "☔"), 65: ("강한 비", "🌧️"),
        71: ("가벼운 눈", "🌨️"), 73: ("눈", "❄️"), 75: ("강한 눈", "❄️"),
        95: ("천둥번개", "⛈️")
    }
    return weather_codes.get(code, ("알 수 없음", "❓"))

def fetch_weather_data():
    lats = ",".join([str(loc['lat']) for loc in LOCATIONS])
    lons = ",".join([str(loc['lon']) for loc in LOCATIONS])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FAlmaty"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    results = []
    # Open-Meteo returns array if multiple coords are queried
    for i, loc in enumerate(LOCATIONS):
        loc_data = data[i] if isinstance(data, list) else data
        # Index 1 is tomorrow's forecast
        tomorrow_code = loc_data['daily']['weathercode'][1]
        t_max = round(loc_data['daily']['temperature_2m_max'][1])
        t_min = round(loc_data['daily']['temperature_2m_min'][1])
        desc, icon = get_weather_desc(tomorrow_code)
        
        results.append({
            "id": loc["id"],
            "name": loc["name"],
            "max": t_max,
            "min": t_min,
            "desc": desc,
            "icon": icon,
            "info": loc["info"]
        })
    return results

def generate_ai_comment(weather_data):
    if not GEMINI_API_KEY:
        return "알마티 인근 국립공원의 내일 날씨 정보입니다. 일교차와 옷차림에 유의하며 안전한 여행 되세요!"
        
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        data_str = ", ".join([f"{w['name']}(최대{w['max']}도/최저{w['min']}도, {w['desc']})" for w in weather_data])
        prompt = f"""
        당신은 카자흐스탄 여행 카페 '카자투'의 날씨 도우미입니다.
        내일의 국립공원 날씨 데이터: {data_str}
        
        이 데이터를 바탕으로 내일 알마티와 근교 국립공원을 방문하는 여행객에게 
        가장 유용한 팁 2~3문장을 작성해주세요. 
        산악지형(콜사이, 카인디, 아씨고원, 침블락)의 추위나, 사막지형(차른, 알틴에멜)의 일교차 등을 강조해주세요.
        출력은 다른 말 없이 딱 필요한 팁 2~3문장만 자연스럽게 적어주세요.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.replace("\n", " ").strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "알마티 인근 국립공원의 내일 날씨 정보입니다. 옷차림에 유의하세요!"

def render_html_to_image(weather_data, ai_comment):
    # 날짜 계산 (내일)
    tomorrow = datetime.now() + timedelta(days=1)
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    day_kor = weekdays[tomorrow.weekday()]
    date_str = tomorrow.strftime("%Y. %m. %d")

    # Jinja2 템플릿 렌더링
    env = FileSystemLoader('templates')
    template = Environment(loader=env).get_template('weather_dashboard.html')
    html_content = template.render(
        locations=weather_data,
        ai_comment=ai_comment,
        day_kor=day_kor,
        date_str=date_str
    )
    
    with open("temp_render.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Playwright로 캡처
    img_path = "daily_weather_card.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1600})
        # 로컬 파일 열기
        page.goto("file://" + os.path.abspath("temp_render.html"))
        # 애니메이션/폰트 로딩 대기
        page.wait_for_timeout(1000) 
        page.screenshot(path=img_path, full_page=True)
        browser.close()
        
    return img_path

def send_telegram_message(img_path, text_caption):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram keys not set. Skipping Telegram delivery.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(img_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': text_caption}
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print("Failed to send Telegram message:", response.text)

if __name__ == "__main__":
    print("Fetching weather data...")
    weather_data = fetch_weather_data()
    
    print("Generating AI comment via Gemini...")
    ai_comment = generate_ai_comment(weather_data)
    
    print("Rendering Image...")
    img_path = render_html_to_image(weather_data, ai_comment)
    
    print("Sending to Telegram...")
    
    # 텔레그램용 텍스트 (옵션)
    text_summary = "⛅ 내일의 카자투 날씨 브리핑\n" + ai_comment
    send_telegram_message(img_path, text_summary)
    
    print("Done!")
