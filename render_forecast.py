"""
render_forecast.py — 주간 예보 카드 독립 렌더 스크립트
============================================================
[수정 이력]
  2026-06-14 : 하드코딩 목 데이터 완전 제거.
               실제 Open-Meteo API 호출로 교체.
               weather_bot.py와 동일한 데이터 파이프라인 사용.
               렌더 후 validate_data.py 교차검증 자동 실행.

[사용법]
  python render_forecast.py              # 주간 카드 렌더 + 검증
  python render_forecast.py --no-verify  # 검증 없이 렌더만
"""

import os
import sys
import asyncio
import argparse
import urllib.request
import json
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

# ── 이 파일의 위치를 기준으로 경로 고정 ─────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCATIONS = [
    {"id": "almaty",     "name": "알마티 시내", "lat": 43.2389, "lon": 76.8897},
    {"id": "shymbulak",  "name": "침블락",      "lat": 43.1283, "lon": 77.0805},
    {"id": "assy",       "name": "아씨고원",    "lat": 43.0858, "lon": 77.8344},
    {"id": "kaindy",     "name": "카인디 호수", "lat": 42.9833, "lon": 78.4667},
    {"id": "kolsay",     "name": "콜사이 호수", "lat": 42.9469, "lon": 78.3242},
    {"id": "charyn",     "name": "차른캐년",    "lat": 43.3444, "lon": 79.0833},
    {"id": "altyn_emel", "name": "알틴에멜",    "lat": 43.8647, "lon": 78.7461},
]

WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']

# ── SVG 아이콘 시스템 — Minimal Line Style (2026-06-15 리디자인) ─────────────────────
# fill 완전 제거, stroke 단색 라인만 사용.
# 구름 색상 단일화 — weather_bot.py와 100% 싱크
_C = 'fill="none" stroke="#64748B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
_CLOUD_PATH = 'M3 15a4 4 0 0 1 1-7.9 6 6 0 0 1 11.4-1.5A3.5 3.5 0 0 1 18 15Z'
_CLOUD_PATH_HIGH = 'M3 13a4 4 0 0 1 1-7.9 6 6 0 0 1 11.4-1.5A3.5 3.5 0 0 1 18 13Z'

_ICON_SUN = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="4.5" stroke="#F59E0B" stroke-width="1.8"/>'
    '<g stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round">'
    '<line x1="12" y1="2" x2="12" y2="5"/>'
    '<line x1="12" y1="19" x2="12" y2="22"/>'
    '<line x1="2" y1="12" x2="5" y2="12"/>'
    '<line x1="19" y1="12" x2="22" y2="12"/>'
    '<line x1="5.3" y1="5.3" x2="7.4" y2="7.4"/>'
    '<line x1="16.6" y1="16.6" x2="18.7" y2="18.7"/>'
    '<line x1="18.7" y1="5.3" x2="16.6" y2="7.4"/>'
    '<line x1="7.4" y1="16.6" x2="5.3" y2="18.7"/>'
    '</g>'
    '</svg>'
)
_ICON_PARTLY_CLOUDY = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none">'
    '<g stroke="#F59E0B" stroke-width="1.6" stroke-linecap="round">'
    '<circle cx="9" cy="7" r="3.5" stroke="#F59E0B" stroke-width="1.6"/>'
    '<line x1="9" y1="1" x2="9" y2="3"/>'
    '<line x1="2" y1="7" x2="4" y2="7"/>'
    '</g>'
    '<path d="M4 18a3.5 3.5 0 0 1 .5-6.9 5 5 0 0 1 9.5-1A3 3 0 0 1 17 18Z" ' + _C + '/>'
    '</svg>'
)
_ICON_CLOUDY = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CLOUD_PATH + '" ' + _C + '/>'
    '</svg>'
)
_ICON_OVERCAST = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CLOUD_PATH + '" ' + _C + '/>'
    '<path d="M2 17h14" stroke="#94A3B8" stroke-width="1.4" stroke-linecap="round"/>'
    '<path d="M4 20h10" stroke="#94A3B8" stroke-width="1.4" stroke-linecap="round"/>'
    '</svg>'
)
_ICON_RAIN = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CLOUD_PATH_HIGH + '" ' + _C + '/>'
    '<g stroke="#60A5FA" stroke-width="1.8" stroke-linecap="round">'
    '<line x1="7" y1="16" x2="5.5" y2="21"/>'
    '<line x1="11" y1="16" x2="9.5" y2="21"/>'
    '<line x1="15" y1="16" x2="13.5" y2="21"/>'
    '</g>'
    '</svg>'
)
_ICON_SNOW = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CLOUD_PATH_HIGH + '" ' + _C + '/>'
    '<g stroke="#93C5FD" stroke-width="1.8" stroke-linecap="round">'
    '<line x1="7" y1="17" x2="7" y2="22"/>'
    '<line x1="5" y1="19" x2="9" y2="19"/>'
    '<line x1="12" y1="17" x2="12" y2="22"/>'
    '<line x1="10" y1="19" x2="14" y2="19"/>'
    '</g>'
    '</svg>'
)
_ICON_STORM = (
    '<svg width="1em" height="1em" viewBox="0 0 24 24">'
    '<path d="' + _CLOUD_PATH_HIGH + '" ' + _C + '/>'
    '<polyline points="12,15 9,20 13,20 10,25" stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    '</svg>'
)

_RAIN_ICON_THRESHOLD = 40  # 이 이상이면 비 아이콘으로 자동 교체

def get_weather_desc(code):
    """WMO 날씨 코드 → SVG 아이콘 (weather_bot.py와 동일 매핑)"""
    mapping = {
        0:  ("맑음",        _ICON_SUN),
        1:  ("구름 조금",   _ICON_PARTLY_CLOUDY),
        2:  ("구름 많음",   _ICON_CLOUDY),
        3:  ("흐림",        _ICON_OVERCAST),
        45: ("안개",        _ICON_OVERCAST), 48: ("안개", _ICON_OVERCAST),
        51: ("가벼운 비",   _ICON_RAIN), 53: ("이슬비", _ICON_RAIN), 55: ("짙은 비", _ICON_RAIN),
        61: ("가벼운 비",   _ICON_RAIN), 63: ("보통 비", _ICON_RAIN), 65: ("강한 비", _ICON_RAIN),
        71: ("가벼운 눈",   _ICON_SNOW), 73: ("보통 눈", _ICON_SNOW), 75: ("강한 눈", _ICON_SNOW),
        77: ("눈발",        _ICON_SNOW), 80: ("소나기", _ICON_RAIN), 81: ("강한 소나기", _ICON_RAIN),
        82: ("폭우",        _ICON_STORM), 85: ("가벼운 눈", _ICON_SNOW), 86: ("강한 눈", _ICON_SNOW),
        95: ("천둥번개",    _ICON_STORM), 96: ("천둥번개", _ICON_STORM), 99: ("천둥번개", _ICON_STORM),
    }
    return mapping.get(code, ("구름 많음", _ICON_CLOUDY))

def get_icon_with_prob(code, prob=0):
    """강수확률 ≥ 40% 이고 비 아이콘이 아닌 경우 비 아이콘으로 자동 교체"""
    desc, icon = get_weather_desc(code)
    if prob >= _RAIN_ICON_THRESHOLD and code < 51:
        icon = _ICON_RAIN
    return desc, icon


# ── 실제 API 데이터 페치 (weather_bot.py fetch_weekly_forecast와 동일 로직) ──
def fetch_weekly_forecast():
    """Open-Meteo API에서 모레~5일 주간 예보를 가져옵니다.
    
    [중요] 이 함수는 weather_bot.py의 fetch_weekly_forecast()와
    완전히 동일한 API 엔드포인트, 파라미터, 인덱스 계산을 사용합니다.
    변경 시 두 파일을 동시에 수정하거나 공유 모듈로 분리하세요.
    """
    lats = ",".join([str(loc["lat"]) for loc in LOCATIONS])
    lons = ",".join([str(loc["lon"]) for loc in LOCATIONS])

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lats}&longitude={lons}"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Asia%2FAlmaty"
        f"&forecast_days=8"
    )

    print(f"🌐 API 호출 중... ({len(LOCATIONS)}개 지역)")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())

    is_multi = isinstance(data, list)

    # index 0=오늘, 1=내일(카드❶), 2~6=모레부터 5일(카드❷)
    start_idx = 2
    num_days  = 5

    results = []
    for i, loc in enumerate(LOCATIONS):
        loc_data = data[i] if is_multi else data

        forecast = []
        for d in range(start_idx, start_idx + num_days):
            try:
                date_str = loc_data["daily"]["time"][d]
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                code = loc_data["daily"]["weathercode"][d]
                prob = min(int(loc_data["daily"]["precipitation_probability_max"][d] or 0), 100)
                _, icon = get_icon_with_prob(code, prob)

                forecast.append({
                    "date":      f"{dt.month}/{dt.day}",
                    "day":       WEEKDAY_KR[dt.weekday()],
                    "full_date": dt,
                    "icon":      icon,
                    "max":       round(loc_data["daily"]["temperature_2m_max"][d]),
                    "min":       round(loc_data["daily"]["temperature_2m_min"][d]),
                    "prob":      prob,
                })
            except (IndexError, KeyError) as e:
                print(f"  ⚠️ {loc['name']} day {d} 데이터 누락: {e}")

        week_max = max(day["max"] for day in forecast) if forecast else 0
        week_min = min(day["min"] for day in forecast) if forecast else 0

        results.append({
            "name":     loc["name"],
            "week_max": week_max,
            "week_min": week_min,
            "forecast": forecast,
        })
        print(f"  ✅ {loc['name']}: {week_max}° / {week_min}°")

    return results


# ── 렌더 ──────────────────────────────────────────────────────
async def render(weekly_data, weekly_advice=""):
    """Jinja2 + Playwright로 주간 예보 카드 렌더링"""
    # 날짜 범위 헤더
    if weekly_data and weekly_data[0]["forecast"]:
        first = weekly_data[0]["forecast"][0]
        last  = weekly_data[0]["forecast"][-1]
        start_dt = first["full_date"]
        end_dt   = last["full_date"]
        date_range = (
            f"{start_dt.strftime('%Y. %m. %d')}"
            f"({WEEKDAY_KR[start_dt.weekday()]})"
            f" ~ "
            f"{end_dt.strftime('%m. %d')}"
            f"({WEEKDAY_KR[end_dt.weekday()]})"
        )
    else:
        date_range = ""

    ai_advice_list = (
        [line.strip().lstrip("-•*").strip() for line in weekly_advice.split("\n") if line.strip()]
        if weekly_advice
        else ["향후 5일간 지역별 날씨 예보입니다. 강수 확률이 높은 날은 실내 활동이나 저지대 투어를 권장합니다."]
    )

    # Jinja2 렌더링
    template_dir = os.path.join(BASE_DIR, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("forecast_option_a.html")
    html_content = template.render(
        date_range=date_range,
        locations=weekly_data,
        ai_advice_list=ai_advice_list,
    )

    # 렌더 후 Jinja2 변수가 남아있으면 즉시 오류
    if "{{" in html_content or "{%" in html_content:
        raise RuntimeError("❌ 렌더된 HTML에 미치환 Jinja2 변수가 있습니다! 템플릿을 확인하세요.")

    # 임시 HTML 저장
    temp_html = os.path.join(BASE_DIR, "temp_forecast_render.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  ✅ HTML 렌더 완료: {temp_html}")

    # Playwright 스크린샷
    img_path = os.path.join(BASE_DIR, "forecast_weather_card.png")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 3000},
                                       device_scale_factor=2)
        await page.goto(f"file://{temp_html}")
        await page.wait_for_timeout(1500)
        await page.locator("#main-card").screenshot(path=img_path)
        await browser.close()
    print(f"  ✅ 이미지 저장: {img_path}")

    return img_path


# ── 메인 ──────────────────────────────────────────────────────
async def main(run_verify=True):
    print("\n" + "="*60)
    print("🌤️  주간 예보 카드 렌더 시작")
    print("="*60)

    # 1) 실제 API에서 데이터 취득
    weekly_data = fetch_weekly_forecast()

    # 2) 렌더
    print("\n🎨 렌더링 중...")
    img_path = await render(weekly_data)

    # 3) 렌더 후 교차검증
    if run_verify:
        print("\n🔍 교차검증 실행 중...")
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, "validate_data.py"), "--weekly"],
            cwd=BASE_DIR
        )
        if result.returncode != 0:
            print("⚠️  검증에서 오류가 감지되었습니다. 위 로그를 확인하세요.")
        else:
            print("✅ 교차검증 완료 — 데이터 일관성 확인!")

    print(f"\n✅ Done → {img_path}\n")
    return img_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-verify", action="store_true", help="교차검증 건너뜀")
    args = parser.parse_args()

    asyncio.run(main(run_verify=not args.no_verify))
