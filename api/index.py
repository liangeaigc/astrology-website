"""
Vercel Serverless Function: 星盘计算
"""

import json
import os
import datetime

def handler(event, context):
    """Vercel Serverless Handler - Vercel Python runtime"""
    
    # CORS preflight
    if event.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    method = event.get('method', 'GET')
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        birth_time = body.get('birth_time')
        city = body.get('city', '上海')
        
        if not birth_time:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '请提供出生时间'})
            }
        
        # 计算星盘
        dt = datetime.datetime.strptime(birth_time, '%Y-%m-%d %H:%M')
        signs = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', 
                 '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']
        month = dt.month
        seed = dt.timetuple().tm_yday
        
        sun_sign = signs[(month - 1) % 12]
        moon_sign = signs[int((seed % 29.5) / 2.5) % 12]
        asc_sign = signs[(month + 1) % 12]
        
        chart_result = {
            'birth_time': birth_time,
            'city': city,
            'sun': f"{sun_sign} {seed % 30}°",
            'moon': f"{moon_sign} {(seed * 2) % 30}°",
            'ascendant': f"{asc_sign} {(seed * 3) % 30}°",
            'midheaven': f"{signs[(month + 4) % 12]} {(seed * 4) % 30}°",
            'planets': {
                'sun': f"{sun_sign} {seed % 30}°",
                'moon': f"{moon_sign} {(seed * 2) % 30}°",
            }
        }
        
        interpretation = f"""🌟 你的星盘显示太阳在 {sun_sign}，月亮在 {moon_sign}，上升星座为 {asc_sign}。

太阳代表你的核心本质，月亮代表你的情感世界，上升星座则是你给外界的第一印象。

这样的配置意味着你是一个脚踏实地、注重实际的人，同时也拥有丰富的内心世界。"""
        
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
