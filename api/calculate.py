"""
Vercel Serverless Function: 测试
"""

import json

def handler(request, context):
    """Test handler for @vercel/python"""
    return {
        'statusCode': 200,
        'headers': {'content-type': 'application/json'},
        'body': '{"message": "Hello from Python!"}'
    }
