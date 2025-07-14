#!/usr/bin/env python3
"""
Heckx AI - Minimal Working Version
"""
import os
import json
import random
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# Simple quote data
QUOTES = [
    {
        "quote": "ความสุขของชีวิตไม่ได้ขึ้นอยู่กับสิ่งที่เกิดขึ้นกับเรา แต่ขึ้นอยู่กับวิธีที่เราตอบสนอง",
        "author": "Epictetus",
        "theme": "resilience"
    },
    {
        "quote": "คุณมีอำนาจเหนือจิตใจของคุณ ไม่ใช่เหตุการณ์ภายนอก",
        "author": "Marcus Aurelius", 
        "theme": "control"
    },
    {
        "quote": "ความยากลำบากเปิดเผยตัวตนที่แท้จริงของเรา",
        "author": "Seneca",
        "theme": "growth"
    }
]

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Heckx AI - Working!</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                text-align: center; 
                padding: 50px; 
                margin: 0;
            }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { font-size: 3em; margin-bottom: 20px; }
            .status { 
                background: rgba(255,255,255,0.1); 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0; 
            }
            button { 
                background: #4CAF50; 
                color: white; 
                border: none; 
                padding: 15px 30px; 
                font-size: 1.1em; 
                border-radius: 5px; 
                cursor: pointer; 
                margin: 10px;
            }
            button:hover { background: #45a049; }
            #result { 
                background: rgba(0,0,0,0.3); 
                padding: 20px; 
                border-radius: 10px; 
                margin-top: 20px; 
                min-height: 100px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Heckx AI</h1>
            <div class="status">
                ✅ <strong>APPLICATION IS WORKING!</strong><br>
                🎯 Minimal version deployed successfully<br>
                📊 Ready for testing
            </div>
            
            <div>
                <button onclick="testQuote()">📝 Get Random Quote</button>
                <button onclick="testHealth()">❤️ Health Check</button>
                <button onclick="testAPI()">🔧 Test API</button>
            </div>
            
            <div id="result">Click a button to test...</div>
        </div>
        
        <script>
            function testQuote() {
                document.getElementById('result').innerHTML = '🔄 Loading...';
                fetch('/api/quote')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = 
                        `📝 <strong>Quote:</strong> ${data.quote}<br>` +
                        `👤 <strong>Author:</strong> ${data.author}<br>` +
                        `🎨 <strong>Theme:</strong> ${data.theme}`;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = '❌ Error: ' + e.message;
                });
            }
            
            function testHealth() {
                document.getElementById('result').innerHTML = '🔄 Checking...';
                fetch('/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = 
                        `✅ <strong>Status:</strong> ${data.status}<br>` +
                        `🚀 <strong>App:</strong> ${data.app}<br>` +
                        `⏰ <strong>Time:</strong> ${data.timestamp}`;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = '❌ Health check failed: ' + e.message;
                });
            }
            
            function testAPI() {
                document.getElementById('result').innerHTML = '🔄 Testing API...';
                fetch('/api/test', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = 
                        `🔧 <strong>API Test:</strong> ${data.message}<br>` +
                        `📊 <strong>Status:</strong> ${data.success ? 'PASS' : 'FAIL'}`;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = '❌ API test failed: ' + e.message;
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'OK',
        'app': 'Heckx AI Minimal',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

@app.route('/api/quote')
def get_quote():
    quote = random.choice(QUOTES)
    return jsonify({
        'quote': quote['quote'],
        'author': quote['author'],
        'theme': quote['theme'],
        'id': random.randint(1000, 9999),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test', methods=['POST'])
def test_api():
    return jsonify({
        'success': True,
        'message': 'API is working perfectly!',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)