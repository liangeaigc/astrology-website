"""
Vercel Serverless Function: 星盘计算
纯 Python 实现，无需 swisseph
"""

import json
import os
import math
import datetime
from functools import lru_cache

# Minimax API configuration
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', 'sk-cp-FdunqMLPAhQ9ERHozFYsKWnVMVWO4aJmmUrBzMrSgUKOWh6RGSjgNgzxYdT4ttTTMBpPoT7tkDBgI-uQ7QKW1F8HwxETf_rImnkJ512uWFpNdrPb4iZD_OE')

# 节气边界（近似，每年略有差异）
SOLAR_TERMS = {
    '小寒': (1, 5), '大寒': (1, 20), '立春': (2, 4), '雨水': (2, 19),
    '惊蛰': (3, 6), '春分': (3, 21), '清明': (4, 5), '谷雨': (4, 20),
    '立夏': (5, 6), '小满': (5, 21), '芒种': (6, 6), '夏至': (6, 21),
    '小暑': (7, 7), '大暑': (7, 23), '立秋': (8, 8), '处暑': (8, 23),
    '白露': (9, 8), '秋分': (9, 23), '寒露': (10, 8), '霜降': (10, 23),
    '立冬': (11, 7), '小雪': (11, 22), '大雪': (12, 7), '冬至': (12, 22)
}

# 星座及其中英文名
ZODIAC_SIGNS = [
    ('白羊座', 'Aries', 3, 21),
    ('金牛座', 'Taurus', 4, 20),
    ('双子座', 'Gemini', 5, 21),
    ('巨蟹座', 'Cancer', 6, 21),
    ('狮子座', 'Leo', 7, 23),
    ('处女座', 'Virgo', 8, 23),
    ('天秤座', 'Libra', 9, 23),
    ('天蝎座', 'Scorpio', 10, 22),
    ('射手座', 'Sagittarius', 11, 22),
    ('摩羯座', 'Capricorn', 12, 22),
    ('水瓶座', 'Aquarius', 1, 20),
    ('双鱼座', 'Pisces', 2, 19),
]

@lru_cache(maxsize=1000)
def get_sun_sign(month, day):
    """根据日期获取太阳星座"""
    for sign_cn, sign_en, start_month, start_day in ZODIAC_SIGNS:
        if month == start_month and day >= start_day:
            return sign_cn
        elif month == start_month + 1 or (start_month == 12 and month == 1):
            # Check if we've passed the boundary
            if start_month == 12:
                if month == 1 and day < start_day:
                    return sign_cn
                elif month == start_month and day >= start_day:
                    return sign_cn
            else:
                prev_sign = ZODIAC_SIGNS[(ZODIAC_SIGNS.index((sign_cn, sign_en, start_month, start_day)) - 1) % 12]
                if month == start_month - 1 or (start_month == 1 and month == 12):
                    if month == 12 and day >= start_day:
                        return sign_cn
                    elif month == start_month - 1:
                        return prev_sign_cn if (prev_sign := ZODIAC_SIGNS[(ZODIAC_SIGNS.index((sign_cn, sign_en, start_month, start_day)) - 1) % 12])
    return '白羊座'  # Default fallback

def calculate_sign_degree(base_sign_date, birth_time):
    """计算行星在星座内的精确度数"""
    # 简化：每颗行星在星座内的位置用随机但一致的分布
    # 真实计算需要天文算法，这里用近似
    dt = datetime.datetime.strptime(birth_time, '%Y-%m-%d %H:%M')
    base = dt.timetuple().tm_yday  # 一年中的第几天
    return (base % 30) + float(dt.minute) / 60

def get_planet_positions(birth_time, city):
    """计算行星位置（简化版）"""
    dt = datetime.datetime.strptime(birth_time, '%Y-%m-%d %H:%M')
    month, day, hour, minute = dt.month, dt.day, dt.hour, dt.minute
    
    # 基础度数（基于日期的伪随机但一致的分布）
    seed = dt.timetuple().tm_yday
    
    # 太阳位置（基于真实星座边界）
    sun_sign = get_sun_sign(month, day)
    sun_degree = ((seed % 30) + minute / 60) % 30
    
    # 月亮位置（每2.5天换一个星座，约29.5天一圈）
    moon_cycle = 29.5
    moon_day = seed % moon_cycle
    moon_sign_index = int(moon_day / 2.5) % 12
    moon_sign = ZODIAC_SIGNS[moon_sign_index][0]
    moon_degree = (moon_day % 2.5) * 12 + minute / 60
    
    # 其他行星（简化：基于固定相位）
    planet_offset = {
        'mercury': 0.3,  # 水星
        'venus': 1.1,    # 金星
        'mars': 2.3,     # 火星
        'jupiter': 4.7,   # 木星
        'saturn': 6.1,   # 土星
        'uranus': 8.5,   # 天王星
        'neptune': 10.2, # 海王星
        'pluto': 11.8,   # 冥王星
    }
    
    planets = {
        'sun': {'sign': sun_sign, 'sign_degree': round(sun_degree, 2)},
        'moon': {'sign': moon_sign, 'sign_degree': round(moon_degree % 30, 2)},
    }
    
    # 计算其他行星
    sun_idx = next(i for i, z in enumerate(ZODIAC_SIGNS) if z[0] == sun_sign)
    
    for planet, offset in planet_offset.items():
        planet_idx = (sun_idx + int(offset * seed / 30)) % 12
        planet_sign = ZODIAC_SIGNS[planet_idx][0]
        planet_degree = (offset * 30 + seed / 30) % 30
        planets[planet] = {'sign': planet_sign, 'sign_degree': round(planet_degree, 2)}
    
    # 上升和天顶
    asc_idx = (sun_idx + 3 + int(hour / 2)) % 12
    mc_idx = (sun_idx + 9 + int(hour / 2)) % 12
    
    return {
        'planets': planets,
        'asc': {'sign': ZODIAC_SIGNS[asc_idx][0], 'sign_degree': round((hour * 30 + minute) / 60 % 30, 2)},
        'mc': {'sign': ZODIAC_SIGNS[mc_idx][0], 'sign_degree': round((hour * 30 + minute) / 60 % 30, 2)},
    }

def calculate_chart_data(birth_time, city, timezone):
    """计算完整星盘"""
    result = get_planet_positions(birth_time, city)
    result['birth_time'] = birth_time
    result['city'] = city
    return result

def get_minimax_interpretation(chart_data, focus_areas=None):
    """调用 Minimax 大模型解读"""
    try:
        import requests
    except ImportError:
        return generate_simple_interpretation(chart_data)
    
    planets = chart_data.get('planets', {})
    sun = planets.get('sun', {})
    moon = planets.get('moon', {})
    asc = chart_data.get('asc', {})
    mc = chart_data.get('mc', {})
    
    prompt = f"""你是一位专业的星盘师。请根据以下星盘数据，为用户提供专业但易懂的解读。

星盘基本信息：
- 太阳：{sun.get('sign', '未知')} {sun.get('sign_degree', '')}°
- 月亮：{moon.get('sign', '未知')} {moon.get('sign_degree', '')}°
- 上升：{asc.get('sign', '未知')} {asc.get('sign_degree', '')}°
- 天顶：{mc.get('sign', '未知')} {mc.get('sign_degree', '')}°

行星分布：
- 水星：{planets.get('mercury', {}).get('sign', '未知')}
- 金星：{planets.get('venus', {}).get('sign', '未知')}
- 火星：{planets.get('mars', {}).get('sign', '未知')}
- 木星：{planets.get('jupiter', {}).get('sign', '未知')}
- 土星：{planets.get('saturn', {}).get('sign', '未知')}

重点解读领域：{focus_areas or '性格、感情、事业'}

请输出一段 200-300 字的星盘解读，要：
1. 温暖有感情，像朋友在说话
2. 突出这个人的天赋和优势
3. 提到可能的挑战和成长点
4. 不要太宿命论，强调个人选择权

直接输出解读内容，不需要标题。"""

    try:
        response = requests.post(
            'https://api.minimax.chat/v1/text/chatcompletion_v2',
            headers={
                'Authorization': f'Bearer {MINIMAX_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'MiniMax-Text-01',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                return content
    except Exception:
        pass
    
    return generate_simple_interpretation(chart_data)

def generate_simple_interpretation(chart_data):
    """简单解读（无API时）"""
    planets = chart_data.get('planets', {})
    sun = planets.get('sun', {})
    moon = planets.get('moon', {})
    asc = chart_data.get('asc', {})
    
    sun_sign = f"{sun.get('sign', '未知')} {sun.get('sign_degree', '')}°"
    moon_sign = f"{moon.get('sign', '未知')} {moon.get('sign_degree', '')}°"
    asc_sign = f"{asc.get('sign', '未知')} {asc.get('sign_degree', '')}°"
    
    return f"""🌟 你的星盘显示太阳在 {sun_sign}，月亮在 {moon_sign}，上升星座为 {asc_sign}。

太阳代表你的核心本质，月亮代表你的情感世界，上升星座则是你给外界的第一印象。

这样的配置意味着你是一个脚踏实地、注重实际的人，同时也拥有丰富的内心世界。你在人际交往中通常给人稳重可靠的印象，但在私下里也有细腻敏感的一面。

建议：多倾听内心的声音，在做重要决定时可以相信自己的直觉。"""

def handler(request):
    """Vercel Serverless Handler"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(request.body or '{}')
        birth_time = body.get('birth_time')
        city = body.get('city', '上海')
        timezone_str = body.get('timezone', 'Asia/Shanghai')
        focus = body.get('focus', '性格、感情、事业')
        
        if not birth_time:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '请提供出生时间'})
            }
        
        # Calculate chart
        chart_data = calculate_chart_data(birth_time, city, timezone_str)
        
        # Format for response
        planets = chart_data.get('planets', {})
        chart_result = {
            'birth_time': chart_data.get('birth_time'),
            'city': chart_data.get('city'),
            'sun': f"{planets.get('sun', {}).get('sign', '未知')} {planets.get('sun', {}).get('sign_degree', '')}°",
            'moon': f"{planets.get('moon', {}).get('sign', '未知')} {planets.get('moon', {}).get('sign_degree', '')}°",
            'ascendant': f"{chart_data.get('asc', {}).get('sign', '未知')} {chart_data.get('asc', {}).get('sign_degree', '')}°",
            'midheaven': f"{chart_data.get('mc', {}).get('sign', '未知')} {chart_data.get('mc', {}).get('sign_degree', '')}°",
            'planets': {
                key: f"{val.get('sign', '未知')} {val.get('sign_degree', '')}°"
                for key, val in planets.items()
            }
        }
        
        # Get AI interpretation
        interpretation = get_minimax_interpretation(chart_data, focus)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': True,
                'chart': chart_result,
                'interpretation': interpretation
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}, ensure_ascii=False)
        }
