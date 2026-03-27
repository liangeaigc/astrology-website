"""
Vercel Serverless Function: 星盘计算
"""
import subprocess
import json
import os
import sys

# Add astrology skills path for ephemeris calculations
sys.path.insert(0, '/var/task')

# Vercel serverless environment - use bundled ephem
try:
    import ephem
except ImportError:
    # Try from common locations
    for path in ['/opt/python/lib/python3.12/site-packages', '/var/task/.venv/lib/python3.12/site-packages']:
        sys.path.insert(0, path)
    
# Minimax API configuration
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', 'sk-cp-FdunqMLPAhQ9ERHozFYsKWnVMVWO4aJmmUrBzMrSgUKOWh6RGSjgNgzxYdT4ttTTMBpPoT7tkDBgI-uQ7QKW1F8HwxETf_rImnkJ512uWFpNdrPb4iZD_OE')

def calculate_chart_data(birth_time, city, timezone):
    """计算星盘数据"""
    try:
        from calculate_chart import calculate_full_chart
        return calculate_full_chart(birth_time, city, timezone)
    except Exception as e:
        # Fallback calculation if script import fails
        import datetime
        import math
        
        # Parse birth time
        dt = datetime.datetime.strptime(birth_time, '%Y-%m-%d %H:%M')
        
        # Simple zodiac calculation (simplified for demo)
        signs = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', 
                 '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']
        
        # Approximate sun sign based on date
        month = dt.month
        day = dt.day
        sign_index = (month - 1 + (1 if day > 20 else 0)) % 12
        
        return {
            'birth_time': birth_time,
            'city': city,
            'planets': {
                'sun': {'sign': signs[sign_index], 'sign_degree': 10.0},
                'moon': {'sign': '巨蟹座', 'sign_degree': 27.0},
                'mercury': {'sign': signs[sign_index], 'sign_degree': 15.0},
                'venus': {'sign': '狮子座', 'sign_degree': 11.0},
                'mars': {'sign': '巨蟹座', 'sign_degree': 27.0},
                'jupiter': {'sign': '天秤座', 'sign_degree': 5.0},
                'saturn': {'sign': '白羊座', 'sign_degree': 3.0},
                'uranus': {'sign': '水瓶座', 'sign_degree': 12.0},
                'neptune': {'sign': '摩羯座', 'sign_degree': 17.0},
                'pluto': {'sign': '射手座', 'sign_degree': 8.0},
            },
            'asc': {'sign': '金牛座', 'sign_degree': 28.0},
            'mc': {'sign': '摩羯座', 'sign_degree': 27.0}
        }

def get_minimax_interpretation(chart_data, focus_areas=None):
    """调用 Minimax 大模型解读"""
    try:
        import requests
    except ImportError:
        return generate_simple_interpretation(chart_data)
    
    prompt = f"""你是一位专业的星盘师。请根据以下星盘数据，为用户提供专业但易懂的解读。

星盘基本信息：
- 太阳：{chart_data.get('planets', {}).get('sun', {}).get('sign', '未知')} {chart_data.get('planets', {}).get('sun', {}).get('sign_degree', '')}°
- 月亮：{chart_data.get('planets', {}).get('moon', {}).get('sign', '未知')} {chart_data.get('planets', {}).get('moon', {}).get('sign_degree', '')}°
- 上升：{chart_data.get('asc', {}).get('sign', '未知')} {chart_data.get('asc', {}).get('sign_degree', '')}°
- 天顶：{chart_data.get('mc', {}).get('sign', '未知')} {chart_data.get('mc', {}).get('sign_degree', '')}°

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
            return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception:
        pass
    
    return generate_simple_interpretation(chart_data)

def generate_simple_interpretation(chart_data):
    """简单解读"""
    planets = chart_data.get('planets', {})
    sun_data = planets.get('sun', {})
    moon_data = planets.get('moon', {})
    asc_data = chart_data.get('asc', {})
    
    sun = f"{sun_data.get('sign', '未知')} {sun_data.get('sign_degree', '')}°"
    moon = f"{moon_data.get('sign', '未知')} {moon_data.get('sign_degree', '')}°"
    asc = f"{asc_data.get('sign', '未知')} {asc_data.get('sign_degree', '')}°"
    
    return f"""🌟 你的星盘显示太阳在 {sun}，月亮在 {moon}，上升星座为 {asc}。

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
