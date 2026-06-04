import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import datetime

WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']

async def render_forecast_sample():
    """주간 예보 카드(카드 ❷) 샘플 렌더링 — 목 데이터 사용"""
    
    # 날짜 계산: 모레부터 7일
    today = datetime.datetime.now()
    start_date = today + datetime.timedelta(days=2)
    
    def make_day_info(offset):
        d = start_date + datetime.timedelta(days=offset)
        return {
            "date": f"{d.month}/{d.day}",
            "day": WEEKDAY_KR[d.weekday()],
        }
    
    # 헤더용 날짜 범위 문자열
    end_date = start_date + datetime.timedelta(days=6)
    date_range = (
        f"{start_date.strftime('%Y. %m. %d')}"
        f"({WEEKDAY_KR[start_date.weekday()]})"
        f" ~ "
        f"{end_date.strftime('%m. %d')}"
        f"({WEEKDAY_KR[end_date.weekday()]})"
    )
    
    # 목 데이터 — 6월 알마티 근교 현실적인 날씨
    locations = [
        {
            "name": "알마티 시내",
            "week_max": 30,
            "week_min": 14,
            "forecast": [
                {**make_day_info(0), "icon": "☀️", "max": 28, "min": 16, "prob": 0},
                {**make_day_info(1), "icon": "🌤️", "max": 27, "min": 15, "prob": 5},
                {**make_day_info(2), "icon": "⛅", "max": 25, "min": 14, "prob": 8},
                {**make_day_info(3), "icon": "🌧️", "max": 22, "min": 15, "prob": 65},
                {**make_day_info(4), "icon": "☁️", "max": 24, "min": 14, "prob": 15},
                {**make_day_info(5), "icon": "☀️", "max": 29, "min": 16, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 30, "min": 17, "prob": 0},
            ]
        },
        {
            "name": "침블락",
            "week_max": 18,
            "week_min": 2,
            "forecast": [
                {**make_day_info(0), "icon": "⛅", "max": 16, "min": 5, "prob": 5},
                {**make_day_info(1), "icon": "☁️", "max": 14, "min": 4, "prob": 8},
                {**make_day_info(2), "icon": "🌧️", "max": 12, "min": 3, "prob": 70},
                {**make_day_info(3), "icon": "🌧️", "max": 10, "min": 2, "prob": 85},
                {**make_day_info(4), "icon": "☁️", "max": 13, "min": 3, "prob": 12},
                {**make_day_info(5), "icon": "⛅", "max": 17, "min": 5, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 18, "min": 6, "prob": 0},
            ]
        },
        {
            "name": "아씨고원",
            "week_max": 16,
            "week_min": -3,
            "forecast": [
                {**make_day_info(0), "icon": "☀️", "max": 14, "min": 0, "prob": 0},
                {**make_day_info(1), "icon": "⛅", "max": 13, "min": -1, "prob": 5},
                {**make_day_info(2), "icon": "❄️", "max": 8, "min": -3, "prob": 75},
                {**make_day_info(3), "icon": "🌧️", "max": 10, "min": -2, "prob": 55},
                {**make_day_info(4), "icon": "☁️", "max": 11, "min": -1, "prob": 10},
                {**make_day_info(5), "icon": "⛅", "max": 15, "min": 1, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 16, "min": 2, "prob": 0},
            ]
        },
        {
            "name": "카인디 호수",
            "week_max": 22,
            "week_min": 4,
            "forecast": [
                {**make_day_info(0), "icon": "☀️", "max": 20, "min": 7, "prob": 0},
                {**make_day_info(1), "icon": "🌤️", "max": 19, "min": 6, "prob": 5},
                {**make_day_info(2), "icon": "🌧️", "max": 16, "min": 5, "prob": 50},
                {**make_day_info(3), "icon": "🌧️", "max": 15, "min": 4, "prob": 72},
                {**make_day_info(4), "icon": "☁️", "max": 17, "min": 5, "prob": 8},
                {**make_day_info(5), "icon": "⛅", "max": 21, "min": 8, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 22, "min": 9, "prob": 0},
            ]
        },
        {
            "name": "콜사이 호수",
            "week_max": 20,
            "week_min": 2,
            "forecast": [
                {**make_day_info(0), "icon": "☀️", "max": 18, "min": 5, "prob": 0},
                {**make_day_info(1), "icon": "⛅", "max": 17, "min": 4, "prob": 5},
                {**make_day_info(2), "icon": "🌧️", "max": 14, "min": 3, "prob": 60},
                {**make_day_info(3), "icon": "🌧️", "max": 13, "min": 2, "prob": 80},
                {**make_day_info(4), "icon": "☁️", "max": 15, "min": 3, "prob": 10},
                {**make_day_info(5), "icon": "⛅", "max": 19, "min": 6, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 20, "min": 7, "prob": 0},
            ]
        },
        {
            "name": "차른캐년",
            "week_max": 35,
            "week_min": 14,
            "forecast": [
                {**make_day_info(0), "icon": "☀️", "max": 33, "min": 18, "prob": 0},
                {**make_day_info(1), "icon": "☀️", "max": 34, "min": 19, "prob": 0},
                {**make_day_info(2), "icon": "⛅", "max": 30, "min": 16, "prob": 5},
                {**make_day_info(3), "icon": "☁️", "max": 28, "min": 14, "prob": 15},
                {**make_day_info(4), "icon": "⛅", "max": 31, "min": 16, "prob": 0},
                {**make_day_info(5), "icon": "☀️", "max": 34, "min": 19, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 35, "min": 20, "prob": 0},
            ]
        },
        {
            "name": "알틴에멜",
            "week_max": 36,
            "week_min": 16,
            "forecast": [
                {**make_day_info(0), "icon": "☀️", "max": 34, "min": 19, "prob": 0},
                {**make_day_info(1), "icon": "☀️", "max": 35, "min": 20, "prob": 0},
                {**make_day_info(2), "icon": "🌤️", "max": 31, "min": 17, "prob": 5},
                {**make_day_info(3), "icon": "⛅", "max": 29, "min": 16, "prob": 10},
                {**make_day_info(4), "icon": "⛅", "max": 32, "min": 18, "prob": 0},
                {**make_day_info(5), "icon": "☀️", "max": 35, "min": 20, "prob": 0},
                {**make_day_info(6), "icon": "☀️", "max": 36, "min": 21, "prob": 0},
            ]
        },
    ]


    ai_advice_list = [
        "주 중반 산악지역(침블락·아씨고원·카인디·콜사이) 비/눈 집중, 이 기간엔 저지대(차른·알틴에멜) 투어 권장",
        "아씨고원 적설 5cm 예상일에는 도로 상태 확인 필수, 방한장비 및 4WD 차량 준비",
        "주 후반 전 지역 맑음 회복, 특히 차른캐년·알틴에멜은 35°C 이상 고온 예상 — 충분한 수분 섭취 필수",
    ]

    # Jinja2 렌더링
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('weather_forecast_light.html')
    html_content = template.render(
        date_range=date_range,
        locations=locations,
        ai_advice_list=ai_advice_list,
    )

    # 임시 HTML 저장
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(base_dir, 'temp_forecast.html')
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Playwright로 스크린샷
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1080, "height": 3000})
        await page.goto(f"file://{temp_path}")
        await page.wait_for_timeout(1500)
        
        img_path = os.path.join(base_dir, 'forecast_weather_card.png')
        await page.locator('#main-card').screenshot(path=img_path)
        await browser.close()
    
    # 프리뷰 HTML 유지
    preview_path = os.path.join(base_dir, 'forecast_preview.html')
    os.rename(temp_path, preview_path)
    
    print(f"✅ Forecast card generated: {img_path}")
    print(f"✅ Preview HTML saved: {preview_path}")

if __name__ == "__main__":
    asyncio.run(render_forecast_sample())
