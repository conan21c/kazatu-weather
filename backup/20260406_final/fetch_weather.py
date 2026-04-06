import urllib.request
import urllib.parse
import json
import datetime

# 알마티 및 근교 핵심 지역별 위도, 경도 좌표
# Open-Meteo API는 입력된 좌표의 고도 데이터를 자동 반영하여 산악 지형 기상에 정확합니다.
LOCATIONS = [
    {"id": "almaty", "name": "알마티 시내", "lat": 43.2389, "lon": 76.8897},
    {"id": "shymbulak", "name": "침블락", "lat": 43.1283, "lon": 77.0805},
    {"id": "assy", "name": "아씨고원", "lat": 43.0858, "lon": 77.8344},
    {"id": "kaindy", "name": "카인디 호수", "lat": 42.9833, "lon": 78.4667},
    {"id": "kolsay", "name": "콜사이 호수", "lat": 42.9469, "lon": 78.3242},
    {"id": "charyn", "name": "차른캐년", "lat": 43.3444, "lon": 79.0833},
    {"id": "altyn_emel", "name": "알틴에멜", "lat": 43.8647, "lon": 78.7461}
]

# WMO Weather interpretation codes
def get_weather_desc(code):
    weather_codes = {
        0: ("맑음", "☀️"),
        1: ("대체로 맑음", "🌤️"), 
        2: ("구름조금", "⛅"), 
        3: ("흐림", "☁️"),
        45: ("안개", "🌫️"), 
        48: ("안개지대", "🌫️"),
        51: ("가벼운 이슬비", "🌧️"), 
        53: ("보통 이슬비", "🌧️"), 
        55: ("짙은 이슬비", "🌧️"),
        61: ("가벼운 비", "☂️"), 
        63: ("보통 비", "☔"), 
        65: ("강한 비", "🌧️"),
        71: ("가벼운 눈", "🌨️"), 
        73: ("보통 눈", "❄️"), 
        75: ("강한 눈", "❄️"),
        95: ("천둥번개", "⛈️")
    }
    return weather_codes.get(code, ("알 수 없음", "❓"))

def fetch_tomorrow_weather():
    lats = ",".join([str(loc['lat']) for loc in LOCATIONS])
    lons = ",".join([str(loc['lon']) for loc in LOCATIONS])
    
    # 내일 날씨를 위한 API 파라미터 구성 (daily 단위 전망)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FAlmaty"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    results = []
    # 여러 지역일 경우 data는 배열 리스트로 옴
    for i, loc in enumerate(LOCATIONS):
        # 배열 형태 응답인지 확인
        loc_data = data[i] if isinstance(data, list) else data
        
        # 'daily' 데이터에서 첫 번째 인덱스(0)는 오늘, 두 번째 인덱스(1)는 내일입니다.
        try:
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
                "icon": icon
            })
        except KeyError:
            print(f"Error parsing data for {loc['name']}")
    
    return results

if __name__ == "__main__":
    weather_data = fetch_tomorrow_weather()
    for w in weather_data:
        print(f"[{w['name']}] {w['icon']} {w['desc']} | 최고 {w['max']}°C / 최저 {w['min']}°C")
