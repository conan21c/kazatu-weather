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

# 2. Location Metadata - ONLY ALTITUDE as requested
LOCATIONS = [
    {"id": "almaty", "name": "알마티 시내", "lat": 43.2389, "lon": 76.8897, "info": "해발 800m"},
    {"id": "shymbulak", "name": "침블락", "lat": 43.1283, "lon": 77.0805, "info": "해발 2200m"},
    {"id": "assy", "name": "아씨고원", "lat": 43.0858, "lon": 77.8344, "info": "해발 2600m"},
    {"id": "kaindy", "name": "카인디 호수", "lat": 42.9833, "lon": 78.4667, "info": "해발 2000m"},
    {"id": "kolsay", "name": "콜사이 호수", "lat": 42.9469, "lon": 78.3242, "info": "해발 1800m"},
    {"id": "charyn", "name": "차른캐년", "lat": 43.3444, "lon": 79.0833, "info": "해발 600m"},
    {"id": "altyn_emel", "name": "알틴에멜", "lat": 43.8647, "lon": 78.7461, "info": "해발 1000m"}
]

def get_weather_desc(code):
    # WMO Weather interpretation codes (WMO) - Unified Line-Art Style
    weather_codes = {
        0: ("맑음", "☀️"), 1: ("구름 조금", "🌤️"), 2: ("구름 많음", "⛅"), 3: ("흐림", "☁️"),
        45: ("안개", "🌫️"), 48: ("안개", "🌫️"),
        51: ("가벼운 비", "🌧️"), 53: ("이슬비", "🌧️"), 55: ("짙은 비", "🌧️"),
        61: ("가벼운 비", "🌧️"), 63: ("보통 비", "☔"), 65: ("강한 비", "🌧️"),
        71: ("가벼운 눈", "🌨️"), 73: ("보통 눈", "❄️"), 75: ("강한 눈", "❄️"),
        77: ("눈발", "❄️"), 80: ("소나기", "🌧️"), 81: ("강한 소나기", "🌧️"), 
        82: ("폭우", "⛈️"), 85: ("가벼운 눈", "🌨️"), 86: ("강한 눈", "❄️"),
        95: ("천둥번개", "⛈️"), 96: ("천둥번개", "⛈️"), 99: ("천둥번개", "⛈️")
    }
    return weather_codes.get(code, ("조금 흐림", "🌤️"))

def fetch_weather_data():
    lats = ",".join([str(loc['lat']) for loc in LOCATIONS])
    lons = ",".join([str(loc['lon']) for loc in LOCATIONS])
    # Fetch hourly data including precipitation probability
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=temperature_2m,weathercode,precipitation_probability&timezone=Asia%2FAlmaty"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    results = []
    # Open-Meteo returns array if multiple coords are queried
    is_multi = isinstance(data, list)
    
    for i, loc in enumerate(LOCATIONS):
        loc_data = data[i] if is_multi else data
        
        # Tomorrow's date start index (assuming 24 hours per day)
        # Hourly data starts from today 00:00. Tomorrow 00:00 is index 24.
        tomorrow_start_idx = 24
        
        # Time points: 9, 12, 15, 18
        target_hours = [9, 12, 15, 18]
        timeline = []
        
        for h in target_hours:
            idx = tomorrow_start_idx + h
            temp = round(loc_data['hourly']['temperature_2m'][idx])
            code = loc_data['hourly']['weathercode'][idx]
            prob = loc_data['hourly']['precipitation_probability'][idx]
            desc, icon = get_weather_desc(code)
            
            timeline.append({
                "time": f"{h:02d}:00",
                "temp": temp,
                "code": code,
                "desc": desc,
                "icon": icon,
                "prob": prob
            })
            
        # Overall max/min for the day (tomorrow)
        t_max = max(loc_data['hourly']['temperature_2m'][tomorrow_start_idx:tomorrow_start_idx+24])
        t_min = min(loc_data['hourly']['temperature_2m'][tomorrow_start_idx:tomorrow_start_idx+24])
        
        results.append({
            "id": loc["id"],
            "name": loc["name"],
            "max": round(t_max),
            "min": round(t_min),
            "timeline": timeline
        })
    return results

def generate_ai_comment(weather_data):
    if not GEMINI_API_KEY:
        return "내일 투어 시 시간별 기온 변화와 강수 확률에 유의하시고, 즐거운 여행 되세요!"
        
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Simplified data string for AI context
        data_summary = []
        for w in weather_data:
            times = ", ".join([f"{t['time']}({t['temp']}도, {t['desc']}, 강수{t['prob']}%)" for t in w['timeline']])
            data_summary.append(f"{w['name']}: {times}")
            
        prompt = f"""
        당신은 카자흐스탄 전문 여행 가이드입니다. 
        내일 투어 지역별 2시간 간격 날씨 데이터: {". ".join(data_summary)}
        
        [지시사항]
        1. 뻔한 인사말이나 장황한 설명은 절대 금지합니다.
        2. 주로 '낮 시간대(08시~18시)' 투어 활동에 직접적으로 영향을 주는 기상 변화만 언급하세요.
        3. 특히 특정 시간대에 비나 눈이 올 확률이 높다면 그 시점을 정확히 짚어주세요.
        4. 실전적인 핵심 조언 2~3줄로만 작성하세요. (최대한 짧고 임팩트 있게)
        
        예시: "내일 알마티는 오후 2시부터 비 확률이 60%로 높으니 우산을 챙기세요. 침블락은 오전 내내 영하권이므로 두꺼운 외투가 필수입니다."
        """
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "내일 지역별 날씨와 강수 확률 정보입니다. 시간대별 예보를 확인하고 안전한 여행 되세요!"

def render_html_to_image(weather_data, ai_comment):
    # 날짜 계산 (내일)
    tomorrow = datetime.now() + timedelta(days=1)
    weekdays_eng = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_eng = weekdays_eng[tomorrow.weekday()]
    date_str = tomorrow.strftime("%Y. %m. %d")

    ai_advice_list = [line.strip().lstrip("-").lstrip("•").lstrip("*").strip() 
                     for line in ai_comment.split("\n") if line.strip()]

    env = FileSystemLoader('templates')
    # Use the new v2 template
    template = Environment(loader=env).get_template('weather_dashboard_dark.html')
    html_content = template.render(
        locations=weather_data,
        ai_advice_list=ai_advice_list,
        day_eng=day_eng,
        date_str=date_str
    )
    
    with open("temp_render.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    img_path = "daily_weather_card.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Adjusted height for more content
        page = browser.new_page(viewport={'width': 1080, 'height': 1500})
        page.goto("file://" + os.path.abspath("temp_render.html"))
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
