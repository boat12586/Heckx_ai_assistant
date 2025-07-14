#!/usr/bin/env python3
"""
Heckx AI - Ultra Minimal Railway Version
Guaranteed to work on Railway platform
"""
import os
import json
import random
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Simple quotes
QUOTES = [
    "ความสุขไม่ขึ้นอยู่กับสิ่งที่เกิดขึ้น แต่ขึ้นอยู่กับการตอบสนอง",
    "คุณมีอำนาจเหนือจิตใจ ไม่ใช่เหตุการณ์ภายนอก", 
    "ความยากลำบากเปิดเผยตัวตนที่แท้จริง",
    "สิ่งที่ขวางทาง จะกลายเป็นทาง",
    "เราทุกข์ในจินตนาการมากกว่าความเป็นจริง"
]

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Heckx AI - Railway Ready</title>
        <style>
            body { font-family: Arial; background: #667eea; color: white; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 10px; }
            button { background: #4CAF50; color: white; border: none; padding: 15px 30px; margin: 10px; border-radius: 5px; cursor: pointer; }
            #result { background: rgba(0,0,0,0.3); padding: 20px; margin-top: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Heckx AI</h1>
            <p>✅ Railway Deployment Success!</p>
            <button onclick="getQuote()">Get Quote</button>
            <button onclick="checkHealth()">Health Check</button>
            <div id="result">Ready to test...</div>
        </div>
        <script>
            function getQuote() {
                fetch('/api/quote').then(r => r.json()).then(data => {
                    document.getElementById('result').innerHTML = 
                        '<h3>Quote:</h3><p>' + data.quote + '</p><p>Time: ' + data.time + '</p>';
                });
            }
            function checkHealth() {
                fetch('/health').then(r => r.json()).then(data => {
                    document.getElementById('result').innerHTML = 
                        '<h3>Health: ' + data.status + '</h3><p>App: ' + data.app + '</p>';
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Ultra simple health check"""
    return jsonify({
        'status': 'OK',
        'app': 'Heckx AI Railway',
        'time': datetime.now().isoformat()
    })

@app.route('/api/quote')
def get_quote():
    """Simple quote endpoint"""
    return jsonify({
        'quote': random.choice(QUOTES),
        'time': datetime.now().isoformat(),
        'id': random.randint(1000, 9999)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)