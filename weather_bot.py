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

WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']

# ============================================================
# SVG 아이콘 시스템 — Emoji-Faithful Filled Style (2026-06-15)
# ☀️🌤️⛅☁️🌧️🌨️⛈️🌫️ 이모지와 시각적으로 동일하게 재현
# filled 색상 + 둥근 구름 형태 + 컬러 포인트
# ============================================================

# 구름 fill 스타일
_CF_W = 'fill="#F1F5F9" stroke="#B8C8D8" stroke-width="0.8" stroke-linejoin="round"'  # 흰 구름
_CF_G = 'fill="#C8D6E0" stroke="#94A3B8" stroke-width="0.8" stroke-linejoin="round"'  # 회색 구름 (비)
_CF_D = 'fill="#8FA3B8" stroke="#64748B" stroke-width="0.8" stroke-linejoin="round"'  # 다크 구름 (폭풍)

# 구름 path — 이모지처럼 둥글고 통통한 닫힌 형태 (viewBox 0 0 24 24 기준)
_CP_W  = 'M2.5 16.5 Q2.5 13 5.5 12 Q6 8.5 10.5 8.5 Q15 8.5 16 12 Q19.5 12 20 15 Q20.5 16.5 18 16.5Z'
_CP_HI = 'M2.5 14.5 Q2.5 11 5.5 10 Q6 6.5 10.5 6.5 Q15 6.5 16 10 Q19.5 10 20 13 Q20.5 14.5 18 14.5Z'

_ICON_SUN = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<circle cx="12" cy="12" r="5.5" fill="#FBBF24"/>'
    '<g stroke="#F59E0B" stroke-width="2" stroke-linecap="round">'
    '<line x1="12" y1="1.5" x2="12" y2="4.5"/>'
    '<line x1="12" y1="19.5" x2="12" y2="22.5"/>'
    '<line x1="1.5" y1="12" x2="4.5" y2="12"/>'
    '<line x1="19.5" y1="12" x2="22.5" y2="12"/>'
    '<line x1="4.7" y1="4.7" x2="6.8" y2="6.8"/>'
    '<line x1="17.2" y1="17.2" x2="19.3" y2="19.3"/>'
    '<line x1="19.3" y1="4.7" x2="17.2" y2="6.8"/>'
    '<line x1="6.8" y1="17.2" x2="4.7" y2="19.3"/>'
    '</g>'
    '</svg>'
)
_ICON_PARTLY_CLOUDY = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<circle cx="9.5" cy="9" r="4" fill="#FBBF24"/>'
    '<g stroke="#F59E0B" stroke-width="1.5" stroke-linecap="round">'
    '<line x1="9.5" y1="2" x2="9.5" y2="4.5"/>'
    '<line x1="2" y1="9" x2="4.5" y2="9"/>'
    '<line x1="4.2" y1="4.2" x2="6" y2="6"/>'
    '</g>'
    '<path d="M5.5 19.5 Q5.5 16.5 8 16 Q8.5 13.5 12 13.5 Q15.5 13.5 16 16 Q18.5 16 19 18 Q19.5 19.5 17.5 19.5Z" ' + _CF_W + '/>'
    '</svg>'
)
_ICON_CLOUDY = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<circle cx="9" cy="9" r="4" fill="#FBBF24"/>'
    '<g stroke="#F59E0B" stroke-width="1.5" stroke-linecap="round">'
    '<line x1="9" y1="2" x2="9" y2="4.5"/>'
    '<line x1="2" y1="9" x2="4.5" y2="9"/>'
    '</g>'
    '<path d="' + _CP_W + '" ' + _CF_W + '/>'
    '</svg>'
)
_ICON_OVERCAST = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="M2 17 Q2 13.5 5 12.5 Q5.5 9 9.5 9 Q13.5 9 14.5 12.5 Q18.5 12.5 19 15.5 Q19.5 17 17 17Z" fill="#E2E8F0" stroke="#94A3B8" stroke-width="0.8" stroke-linejoin="round"/>'
    '</svg>'
)
_ICON_FOG = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="M2 14.5 Q2 11 5 10 Q5.5 6.5 9.5 6.5 Q13.5 6.5 14.5 10 Q18.5 10 19 13 Q19.5 14.5 17 14.5Z" fill="#E2E8F0" stroke="#94A3B8" stroke-width="0.8" stroke-linejoin="round"/>'
    '<g stroke="#94A3B8" stroke-width="2" stroke-linecap="round">'
    '<line x1="3" y1="17.5" x2="19" y2="17.5"/>'
    '<line x1="5" y1="20.5" x2="17" y2="20.5"/>'
    '</g>'
    '</svg>'
)
_ICON_RAIN = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CP_HI + '" ' + _CF_G + '/>'
    '<g stroke="#60A5FA" stroke-width="2" stroke-linecap="round">'
    '<line x1="7" y1="17" x2="5.5" y2="21"/>'
    '<line x1="12" y1="17" x2="10.5" y2="21"/>'
    '<line x1="17" y1="17" x2="15.5" y2="21"/>'
    '</g>'
    '</svg>'
)
_ICON_SNOW = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CP_HI + '" ' + _CF_G + '/>'
    '<g stroke="#93C5FD" stroke-width="2" stroke-linecap="round">'
    '<line x1="7" y1="17" x2="7" y2="22"/>'
    '<line x1="4.5" y1="19.5" x2="9.5" y2="19.5"/>'
    '<line x1="15" y1="17" x2="15" y2="22"/>'
    '<line x1="12.5" y1="19.5" x2="17.5" y2="19.5"/>'
    '</g>'
    '</svg>'
)
_ICON_STORM = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="M2.5 14 Q2.5 10.5 5.5 9.5 Q6 6 10.5 6 Q15 6 16 9.5 Q19.5 9.5 20 12.5 Q20.5 14 18 14Z" ' + _CF_D + '/>'
    '<polyline points="13,15 10,21 14,21 11,27" fill="none" stroke="#FCD34D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

# 강수확률 기준값 — 이 이상이면 비 아이콘으로 자동 교체
_RAIN_ICON_THRESHOLD = 40

def get_weather_desc(code):
    """WMO 날씨 코드 → (설명, SVG 아이콘 문자열) 반환."""
    weather_codes = {
        0:  ("맑음",       _ICON_SUN),
        1:  ("구름 조금",  _ICON_PARTLY_CLOUDY),
        2:  ("구름 많음",  _ICON_CLOUDY),
        3:  ("흐림",       _ICON_OVERCAST),
        45: ("안개",       _ICON_FOG), 48: ("안개", _ICON_FOG),
        51: ("가벼운 비",  _ICON_RAIN), 53: ("이슬비", _ICON_RAIN), 55: ("짙은 비", _ICON_RAIN),
        61: ("가벼운 비",  _ICON_RAIN), 63: ("보통 비", _ICON_RAIN), 65: ("강한 비", _ICON_RAIN),
        71: ("가벼운 눈",  _ICON_SNOW), 73: ("보통 눈", _ICON_SNOW), 75: ("강한 눈", _ICON_SNOW),
        77: ("눈발",       _ICON_SNOW), 80: ("소나기", _ICON_RAIN), 81: ("강한 소나기", _ICON_RAIN),
        82: ("폭우",       _ICON_STORM), 85: ("가벼운 눈", _ICON_SNOW), 86: ("강한 눈", _ICON_SNOW),
        95: ("천둥번개",   _ICON_STORM), 96: ("천둥번개", _ICON_STORM), 99: ("천둥번개", _ICON_STORM),
    }
    return weather_codes.get(code, ("구름 많음", _ICON_CLOUDY))

def get_icon_with_prob(code, prob=0):
    """강수확률 ≥ 40% 이고 비/눈/폭풍 코드가 아닌 경우 비 아이콘으로 자동 교체."""
    desc, icon = get_weather_desc(code)
    if prob >= _RAIN_ICON_THRESHOLD and code < 51:
        icon = _ICON_RAIN
        desc = f"{desc} (강수 {prob}%)"
    return desc, icon

# ============================================================
# 카드 ❶: 일별 상세 (기존 — 변경 없음)
# ============================================================

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
            prob = min(int(loc_data['hourly']['precipitation_probability'][idx] or 0), 100)
            desc, icon = get_icon_with_prob(code, prob)
            
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

def render_daily_card(weather_data, ai_comment):
    """카드 ❶: 일별 상세 카드 렌더링 (기존 로직)"""
    # 날짜 계산 (내일)
    tomorrow = datetime.now() + timedelta(days=1)
    weekdays_eng = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_eng = weekdays_eng[tomorrow.weekday()]
    date_str = tomorrow.strftime("%Y. %m. %d")

    ai_advice_list = [line.strip().lstrip("-").lstrip("•").lstrip("*").strip() 
                     for line in ai_comment.split("\n") if line.strip()]

    env = FileSystemLoader('templates')
    template = Environment(loader=env).get_template('weather_dashboard_light.html')
    html_content = template.render(
        locations=weather_data,
        ai_advice_list=ai_advice_list,
        day_eng=day_eng,
        date_str=date_str
    )

    # ── 렌더 후 무결성 검사: Jinja2 변수 미치환 감지 ──────────────
    if "{{" in html_content or "{%" in html_content:
        raise RuntimeError(
            "[카드❶] 렌더된 HTML에 미치환 Jinja2 변수가 있습니다!\n"
            "템플릿(weather_dashboard_light.html)의 변수명과 "
            "render() 인자를 확인하세요."
        )
    # ─────────────────────────────────────────────────────────────
    
    with open("temp_render.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    img_path = "daily_weather_card.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1800}, device_scale_factor=2)
        page.goto("file://" + os.path.abspath("temp_render.html"))
        page.wait_for_timeout(1000) 
        page.locator('#main-card').screenshot(path=img_path)
        browser.close()
        
    return img_path

# ============================================================
# 카드 ❷: 주간 예보 (신규)
# ============================================================

def fetch_weekly_forecast():
    """모레부터 7일간 daily 예보 데이터를 가져옵니다."""
    lats = ",".join([str(loc['lat']) for loc in LOCATIONS])
    lons = ",".join([str(loc['lon']) for loc in LOCATIONS])
    
    # daily 단위: 날씨코드, 최고/최저기온, 강수확률(최대)
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
    
    # 날짜 계산: 모레(index 2)부터 5일
    start_idx = 2  # index 0=오늘, 1=내일(카드❶), 2=모레(카드❷ 시작)
    num_days = 5
    
    results = []
    for i, loc in enumerate(LOCATIONS):
        loc_data = data[i] if is_multi else data
        
        forecast = []
        for d in range(start_idx, start_idx + num_days):
            try:
                date_str = loc_data['daily']['time'][d]  # "2026-06-06"
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                
                code = loc_data['daily']['weathercode'][d]
                prob = min(int(loc_data['daily']['precipitation_probability_max'][d] or 0), 100)
                _, icon = get_icon_with_prob(code, prob)
                
                forecast.append({
                    "date": f"{dt.month}/{dt.day}",
                    "day": WEEKDAY_KR[dt.weekday()],
                    "full_date": dt,
                    "icon": icon,
                    "max": round(loc_data['daily']['temperature_2m_max'][d]),
                    "min": round(loc_data['daily']['temperature_2m_min'][d]),
                    "prob": prob,
                })
            except (IndexError, KeyError) as e:
                print(f"Warning: Missing data for {loc['name']} day {d}: {e}")
        
        # 주간 최고/최저 범위
        week_max = max(day["max"] for day in forecast) if forecast else 0
        week_min = min(day["min"] for day in forecast) if forecast else 0
        
        results.append({
            "name": loc["name"],
            "week_max": week_max,
            "week_min": week_min,
            "forecast": forecast,
        })
    
    return results

def generate_weekly_advice(weekly_data):
    """주간 날씨 데이터를 기반으로 AI 주간 조언을 생성합니다."""
    if not GEMINI_API_KEY:
        return "향후 5일간 지역별 날씨 예보를 확인하시고 투어 계획에 참고하세요."
    
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        data_summary = []
        for loc in weekly_data:
            days_str = ", ".join([
                f"{d['date']}({d['day']}) {d['icon']} {d['max']}°/{d['min']}° 강수{d['prob']}%"
                for d in loc['forecast']
            ])
            data_summary.append(f"{loc['name']}: {days_str}")
        
        prompt = f"""
        당신은 카자흐스탄 전문 여행 가이드입니다.
        향후 5일간 투어 지역별 일일 날씨 예보 데이터:
        {chr(10).join(data_summary)}
        
        [지시사항]
        1. 뻔한 인사말이나 장황한 설명은 절대 금지합니다.
        2. 5일 전체를 조망하여, 투어 계획 수립에 도움이 되는 핵심 조언을 하세요.
        3. 어떤 날이 투어하기 좋은지, 어떤 날은 피해야 하는지 명확히 짚어주세요.
        4. 산악지대(침블락, 아씨고원)와 저지대(차른캐년, 알틴에멜)의 기상 차이를 고려하세요.
        5. 실전적인 핵심 조언 2~3줄로만 작성하세요. (최대한 짧고 임팩트 있게)
        
        예시: "이번 주 수~목 산악지대 비/눈 예상, 이 기간엔 차른캐년 투어가 최적입니다. 금요일부터 전 지역 맑음, 주말 콜사이 호수 방문을 추천합니다."
        """
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error (weekly): {e}")
        return "향후 5일간 지역별 날씨 예보입니다. 강수 확률이 높은 날은 실내 활동이나 저지대 투어를 권장합니다."

def render_forecast_card(weekly_data, weekly_advice):
    """카드 ❷: 주간 예보 카드 렌더링"""
    # 날짜 범위 계산
    if weekly_data and weekly_data[0]['forecast']:
        first_day = weekly_data[0]['forecast'][0]
        last_day = weekly_data[0]['forecast'][-1]
        
        start_dt = first_day['full_date']
        end_dt = last_day['full_date']
        
        date_range = (
            f"{start_dt.strftime('%Y. %m. %d')}"
            f"({WEEKDAY_KR[start_dt.weekday()]})"
            f" ~ "
            f"{end_dt.strftime('%m. %d')}"
            f"({WEEKDAY_KR[end_dt.weekday()]})"
        )
    else:
        date_range = ""
    
    ai_advice_list = [line.strip().lstrip("-").lstrip("•").lstrip("*").strip() 
                     for line in weekly_advice.split("\n") if line.strip()]
    
    env = FileSystemLoader('templates')
    template = Environment(loader=env).get_template('forecast_option_a.html')
    html_content = template.render(
        date_range=date_range,
        locations=weekly_data,
        ai_advice_list=ai_advice_list,
    )

    # ── 렌더 후 무결성 검사: Jinja2 변수 미치환 감지 ──────────────
    if "{{" in html_content or "{%" in html_content:
        raise RuntimeError(
            "[카드❷] 렌더된 HTML에 미치환 Jinja2 변수가 있습니다!\n"
            "템플릿(forecast_option_a.html)의 변수명과 "
            "render() 인자를 확인하세요."
        )
    # ─────────────────────────────────────────────────────────────
    
    with open("temp_forecast_render.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    img_path = "forecast_weather_card.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 3000}, device_scale_factor=2)
        page.goto("file://" + os.path.abspath("temp_forecast_render.html"))
        page.wait_for_timeout(1500)
        page.locator('#main-card').screenshot(path=img_path)
        browser.close()
    
    return img_path

# ============================================================
# 텔레그램 발송
# ============================================================

def send_telegram_message(img_path, text_caption):
    """단일 이미지 발송 (폴백용)"""
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

def send_telegram_media_group(img_paths, caption):
    """2장 이미지를 앨범(미디어 그룹)으로 발송"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram keys not set. Skipping Telegram delivery.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMediaGroup"
    
    files = {}
    media = []
    
    for idx, img_path in enumerate(img_paths):
        file_key = f"photo{idx}"
        files[file_key] = open(img_path, 'rb')
        
        media_item = {
            "type": "photo",
            "media": f"attach://{file_key}",
        }
        # 캡션은 첫 번째 이미지에만 (텔레그램 미디어그룹 규칙)
        if idx == 0:
            media_item["caption"] = caption
        
        media.append(media_item)
    
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'media': json.dumps(media),
    }
    
    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            print("Telegram media group sent successfully.")
        else:
            print(f"Failed to send media group: {response.text}")
            # 폴백: 개별 발송
            print("Falling back to individual photo sends...")
            for img_path in img_paths:
                send_telegram_message(img_path, caption)
    finally:
        # 파일 핸들 닫기
        for f in files.values():
            f.close()

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    import subprocess

    # ── 카드 ❶: 일별 상세 (내일) ──
    print("📋 [카드❶] Fetching daily weather data...")
    weather_data = fetch_weather_data()
    
    print("🤖 [카드❶] Generating AI comment via Gemini...")
    ai_comment = generate_ai_comment(weather_data)
    
    print("🎨 [카드❶] Rendering daily card...")
    daily_img = render_daily_card(weather_data, ai_comment)
    
    # ── 카드 ❷: 주간 예보 (모레~7일) ──
    print("📋 [카드❷] Fetching weekly forecast data...")
    weekly_data = fetch_weekly_forecast()
    
    print("🤖 [카드❷] Generating weekly AI advice via Gemini...")
    weekly_advice = generate_weekly_advice(weekly_data)
    
    print("🎨 [카드❷] Rendering forecast card...")
    forecast_img = render_forecast_card(weekly_data, weekly_advice)

    # ── 배포 전 교차검증 ──────────────────────────────────────────
    print("\n🔍 [검증] 렌더 결과 교차검증 실행 중...")
    validate_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_data.py")
    verify_result = subprocess.run(
        [__import__('sys').executable, validate_script],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if verify_result.returncode != 0:
        print("⚠️  [검증] 데이터 불일치 감지 — 텔레그램 발송 전 로그를 확인하세요.")
    else:
        print("✅ [검증] 데이터 일관성 확인 완료!")
    # ─────────────────────────────────────────────────────────────

    # ── 텔레그램 발송: 2장 앨범 ──
    print("📤 Sending 2 cards to Telegram as album...")
    
    caption = (
        "⛅ 카자투 날씨 브리핑\n"
        f"📋 카드1: 내일 상세 | 카드2: 향후 7일 예보\n\n"
        f"{ai_comment}"
    )
    
    send_telegram_media_group(
        [daily_img, forecast_img],
        caption
    )
    
    print("✅ Done!")
