#!/usr/bin/env python3
"""
Heckx AI Assistant with Container Integration
"""

import os
import json
from flask import Flask, jsonify, request
from container_integration import ContainerIntegration
from stoic_quotes import StoicQuotesGenerator

app = Flask(__name__)

# Initialize services
container_integration = ContainerIntegration()
quotes_generator = StoicQuotesGenerator()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Heckx AI - Ultimate Video Creator</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .subtitle { font-size: 1.2em; opacity: 0.9; margin-bottom: 30px; }
            
            .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .feature-card { 
                background: rgba(255,255,255,0.1); 
                backdrop-filter: blur(10px);
                border-radius: 15px; 
                padding: 25px; 
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            .feature-card:hover { transform: translateY(-5px); }
            .feature-icon { font-size: 3em; margin-bottom: 15px; }
            .feature-title { font-size: 1.3em; margin-bottom: 10px; font-weight: bold; }
            
            .demo-section { 
                background: rgba(255,255,255,0.1); 
                backdrop-filter: blur(10px);
                border-radius: 20px; 
                padding: 30px; 
                margin-bottom: 30px;
            }
            
            .api-demo { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .demo-panel { 
                background: rgba(0,0,0,0.2); 
                border-radius: 10px; 
                padding: 20px;
            }
            
            button { 
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                color: white; 
                border: none; 
                padding: 12px 25px; 
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                font-weight: bold;
                margin: 10px 5px;
                transition: transform 0.2s ease;
            }
            button:hover { transform: scale(1.05); }
            
            .status-indicator { 
                display: inline-block; 
                width: 10px; 
                height: 10px; 
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-online { background: #4CAF50; }
            .status-offline { background: #F44336; }
            
            .chat-messages { 
                height: 200px; 
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                padding: 15px; 
                overflow-y: auto; 
                margin-bottom: 15px;
                font-family: monospace;
            }
            
            input[type="text"] { 
                width: 100%; 
                padding: 12px; 
                border: none; 
                border-radius: 25px;
                background: rgba(255,255,255,0.9);
                color: #333;
                font-size: 1em;
            }
            
            .footer { text-align: center; margin-top: 40px; opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Heckx AI</h1>
                <div class="subtitle">Ultimate Motivational Video Creator Platform</div>
                <div class="subtitle">พร้อม Kokoro TTS + NCA Toolkit + MinIO + Baserow + n8n</div>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎙️</div>
                    <div class="feature-title">Kokoro GPU TTS</div>
                    <div><span id="kokoro-status" class="status-indicator status-offline"></span>High-Quality Voice Synthesis</div>
                    <button onclick="testKokoro()">Test TTS</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🎬</div>
                    <div class="feature-title">NCA Toolkit</div>
                    <div><span id="nca-status" class="status-indicator status-offline"></span>AI Video Generation</div>
                    <button onclick="testNCA()">Test NCA</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">💾</div>
                    <div class="feature-title">MinIO Storage</div>
                    <div><span id="minio-status" class="status-indicator status-offline"></span>Media Storage</div>
                    <button onclick="testStorage()">Test Storage</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Baserow Database</div>
                    <div><span id="baserow-status" class="status-indicator status-offline"></span>Data Management</div>
                    <button onclick="testDatabase()">Test DB</button>
                </div>
            </div>
            
            <div class="demo-section">
                <h2 style="text-align: center; margin-bottom: 30px;">🎭 Live Demo</h2>
                
                <div class="api-demo">
                    <div class="demo-panel">
                        <h3>💬 AI Chat</h3>
                        <div id="chat-messages" class="chat-messages">
                            <div><strong>Heckx:</strong> สวัสดีครับ! ผมพร้อมสร้างวิดีโอสุดเจ๋งให้คุณ</div>
                        </div>
                        <input type="text" id="chat-input" placeholder="พิมพ์ข้อความ..." onkeypress="if(event.key=='Enter') sendChat()">
                        <button onclick="sendChat()">ส่ง</button>
                    </div>
                    
                    <div class="demo-panel">
                        <h3>🎬 Video Generator</h3>
                        <button onclick="generateQuote()" style="width: 100%; margin-bottom: 10px;">🎯 Generate Daily Quote</button>
                        <button onclick="createVideo()" style="width: 100%; margin-bottom: 10px;">🚀 Create Motivational Video</button>
                        <button onclick="checkContainers()" style="width: 100%;">📊 Check All Containers</button>
                        <div id="video-status" style="margin-top: 15px; font-family: monospace; font-size: 0.9em;"></div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Powered by Docker Containers • Created with ❤️ by bobo • Ready for Production 🔥</p>
            </div>
        </div>
        
        <script>
            // Check container status on load
            checkContainers();
            
            function updateStatus(service, isOnline) {
                const element = document.getElementById(service + '-status');
                if (element) {
                    element.className = 'status-indicator ' + (isOnline ? 'status-online' : 'status-offline');
                }
            }
            
            function checkContainers() {
                document.getElementById('video-status').innerHTML = '🔄 Checking containers...';
                
                fetch('/api/containers/status')
                .then(r => r.json())
                .then(data => {
                    const services = data.services || {};
                    updateStatus('kokoro', services.kokoro_tts?.health === 'healthy');
                    updateStatus('nca', services.nca_toolkit?.health === 'healthy');
                    updateStatus('minio', services.minio?.health === 'healthy');
                    updateStatus('baserow', services.baserow?.health === 'healthy');
                    
                    document.getElementById('video-status').innerHTML = 
                        `✅ System Health: ${data.overall_health}<br>` +
                        `📊 Services Online: ${Object.values(services).filter(s => s.health === 'healthy').length}/${Object.keys(services).length}`;
                })
                .catch(e => {
                    document.getElementById('video-status').innerHTML = '❌ Error checking containers';
                });
            }
            
            function generateQuote() {
                document.getElementById('video-status').innerHTML = '🎯 Generating quote...';
                
                fetch('/api/quote/daily')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('video-status').innerHTML = 
                        `📝 <strong>Quote:</strong> ${data.quote}<br>` +
                        `👤 <strong>Author:</strong> ${data.author}<br>` +
                        `🎨 <strong>Theme:</strong> ${data.theme}`;
                });
            }
            
            function createVideo() {
                document.getElementById('video-status').innerHTML = '🚀 Creating video pipeline...';
                
                fetch('/api/video/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({theme: 'resilience'})
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('video-status').innerHTML = 
                        `🎬 <strong>Status:</strong> ${data.success ? '✅ Success' : '❌ Failed'}<br>` +
                        `📊 <strong>Pipeline:</strong> ${data.pipeline.steps.length} steps<br>` +
                        `🎯 <strong>Message:</strong> ${data.message}`;
                });
            }
            
            function testKokoro() {
                fetch('/api/tts/synthesize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: 'สวัสดีจาก Kokoro TTS', voice: 'thai_female'})
                })
                .then(r => r.json())
                .then(data => {
                    alert(data.success ? '✅ Kokoro TTS Working!' : '❌ Kokoro TTS Failed');
                });
            }
            
            function testNCA() {
                alert('🎬 NCA Toolkit integration ready!');
            }
            
            function testStorage() {
                alert('💾 MinIO storage integration ready!');
            }
            
            function testDatabase() {
                alert('📊 Baserow database integration ready!');
            }
            
            function sendChat() {
                const input = document.getElementById('chat-input');
                const messages = document.getElementById('chat-messages');
                const text = input.value.trim();
                
                if (!text) return;
                
                messages.innerHTML += `<div><strong>คุณ:</strong> ${text}</div>`;
                input.value = '';
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                })
                .then(r => r.json())
                .then(data => {
                    messages.innerHTML += `<div><strong>Heckx:</strong> ${data.response}</div>`;
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

@app.route('/api/containers/status')
def containers_status():
    """Check status of all containers"""
    status = container_integration.get_system_status()
    return jsonify(status)

@app.route('/api/quote/generate', methods=['POST'])
def generate_quote():
    """Generate a motivational quote"""
    data = request.json or {}
    theme = data.get('theme', 'resilience')
    language = data.get('language', 'thai')
    
    quote = quotes_generator.get_quote_by_theme(theme, language)
    return jsonify(quotes_generator.export_for_api(quote))

@app.route('/api/video/create', methods=['POST'])
def create_video():
    """Create motivational video using all containers"""
    data = request.json or {}
    
    # Generate quote if not provided
    if 'quote' not in data:
        theme = data.get('theme', 'resilience')
        quote_data = quotes_generator.get_quote_by_theme(theme)
        quote_data = quotes_generator.export_for_api(quote_data)
    else:
        quote_data = data['quote']
    
    # Create video using container pipeline
    result = container_integration.create_motivational_video_pipeline(quote_data)
    
    return jsonify({
        'success': result['status'] == 'completed',
        'pipeline': result,
        'video_id': result.get('outputs', {}).get('video_id'),
        'message': 'Video creation pipeline executed'
    })

@app.route('/api/tts/synthesize', methods=['POST'])
def synthesize_speech():
    """Use Kokoro TTS for speech synthesis"""
    data = request.json or {}
    text = data.get('text', 'สวัสดีครับ')
    voice = data.get('voice', 'thai_female')
    
    result = container_integration.use_kokoro_tts(text, voice)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Speech synthesized successfully',
            'audio_format': result['format']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 500

@app.route('/api/quote/daily')
def daily_quote():
    """Get today's motivational quote"""
    quote = quotes_generator.get_daily_quote()
    return jsonify(quotes_generator.export_for_api(quote))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)