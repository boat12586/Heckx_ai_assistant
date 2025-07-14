#!/usr/bin/env python3
"""
Ultra-minimal Heckx AI Assistant for Railway
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Heckx AI</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; margin: 40px; text-align: center; }
            .chat { max-width: 600px; margin: 0 auto; }
            input { width: 70%; padding: 10px; margin: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; }
            .messages { height: 300px; border: 1px solid #ddd; padding: 20px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="chat">
            <h1>🤖 Heckx AI Assistant</h1>
            <div id="messages" class="messages">
                <p><strong>Heckx:</strong> สวัสดีครับ! ผมคือ Heckx AI ผู้ช่วยของคุณ</p>
            </div>
            <div>
                <input type="text" id="input" placeholder="พิมพ์ข้อความ..." onkeypress="if(event.key=='Enter') send()">
                <button onclick="send()">ส่ง</button>
            </div>
        </div>
        
        <script>
            function send() {
                const input = document.getElementById('input');
                const messages = document.getElementById('messages');
                const text = input.value.trim();
                
                if (!text) return;
                
                messages.innerHTML += `<p><strong>คุณ:</strong> ${text}</p>`;
                input.value = '';
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                })
                .then(r => r.json())
                .then(data => {
                    messages.innerHTML += `<p><strong>Heckx:</strong> ${data.response}</p>`;
                    messages.scrollTop = messages.scrollHeight;
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    from flask import request
    
    data = request.json
    user_msg = data.get('message', '').lower()
    
    # Simple responses
    if 'สวัสดี' in user_msg or 'hello' in user_msg:
        response = 'สวัสดีครับ! ยินดีที่ได้รู้จักคุณ'
    elif 'คุณคือใคร' in user_msg or 'who are you' in user_msg:
        response = 'ผมคือ Heckx AI ผู้ช่วยที่สร้างโดย bobo ครับ'
    elif 'ขอบคุณ' in user_msg or 'thank' in user_msg:
        response = 'ยินดีครับ! มีอะไรให้ช่วยอีกไหม?'
    elif 'ลาก่อน' in user_msg or 'bye' in user_msg:
        response = 'ลาก่อนครับ! แวะมาคุยกันใหม่นะ'
    else:
        response = f'ได้รับข้อความ: "{data.get("message")}" ขอบคุณที่คุยกับผมครับ!'
    
    return jsonify({'response': response})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'app': 'Heckx AI'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)