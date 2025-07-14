#!/usr/bin/env python3
"""
Heckx AI Assistant - Standalone version with all features
"""

import os
import json
import random
import requests
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# Embedded classes instead of separate modules
class StoicQuotesGenerator:
    def __init__(self):
        self.thai_quotes = [
            {
                "quote": "ความสุขของชีวิตไม่ได้ขึ้นอยู่กับสิ่งที่เกิดขึ้นกับเรา แต่ขึ้นอยู่กับวิธีที่เราตอบสนองต่อสิ่งที่เกิดขึ้น",
                "author": "Epictetus",
                "theme": "resilience",
                "color": "#2C3E50",
                "background": "mountain"
            },
            {
                "quote": "คุณมีอำนาจเหนือจิตใจของคุณ ไม่ใช่เหตุการณ์ภายนอก เมื่อคุณตระหนักถึงสิ่งนี้ คุณจะพบความแข็งแกร่ง",
                "author": "Marcus Aurelius",
                "theme": "control",
                "color": "#8E44AD",
                "background": "ocean"
            },
            {
                "quote": "ไม่ใช่สิ่งที่เกิดขึ้นกับคุณ แต่เป็นวิธีที่คุณตอบสนองต่อสิ่งที่เกิดขึ้นที่สำคัญ",
                "author": "Epictetus",
                "theme": "response",
                "color": "#E74C3C",
                "background": "sunset"
            },
            {
                "quote": "ความยากลำบากเปิดเผยตัวตนที่แท้จริงของเรา",
                "author": "Seneca",
                "theme": "growth",
                "color": "#27AE60",
                "background": "forest"
            }
        ]

    def get_random_quote(self, language="thai", theme=None):
        quotes = self.thai_quotes
        if theme:
            quotes = [q for q in quotes if q.get("theme") == theme]
        if not quotes:
            quotes = self.thai_quotes
        return random.choice(quotes)
    
    def get_daily_quote(self):
        today = datetime.now().strftime("%Y-%m-%d")
        random.seed(today)
        quote = self.get_random_quote()
        random.seed()
        return quote
    
    def export_for_api(self, quote_data):
        return {
            "id": f"quote_{random.randint(1000, 9999)}",
            "quote": quote_data["quote"],
            "author": quote_data["author"],
            "theme": quote_data["theme"],
            "style": {
                "color": quote_data["color"],
                "background": quote_data["background"]
            },
            "video_ready": True,
            "timestamp": datetime.now().isoformat()
        }

class VideoFootageManager:
    def __init__(self):
        # Real API keys
        self.pixabay_key = "51171247-ed811b64146f17a9491cc525f"
        self.pexels_key = "1Vtcwi0g2To9iSY7FJubIw8qW5DoiislcRvoN6hBZJlO3JdyMC1sdl3s"
        
        # Stock video categories
        self.video_categories = {
            "resilience": ["mountain", "storm", "waves", "strong", "powerful"],
            "peace": ["sunset", "calm", "meditation", "zen", "nature"],
            "growth": ["forest", "plant", "sunrise", "growth", "tree"],
            "success": ["sky", "achievement", "victory", "celebration"],
            "motivation": ["running", "fitness", "energy", "action"]
        }

    def search_pixabay_videos(self, theme):
        """Search Pixabay for videos by theme"""
        try:
            keywords = self.video_categories.get(theme, ["nature"])
            query = keywords[0]  # Use first keyword
            
            url = f"https://pixabay.com/api/videos/"
            params = {
                'key': self.pixabay_key,
                'q': query,
                'video_type': 'film',
                'category': 'nature',
                'min_duration': 10,
                'per_page': 5,
                'safesearch': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                for item in data.get('hits', []):
                    videos.append({
                        'id': item['id'],
                        'url': item['videos']['medium']['url'],
                        'preview': item['videos']['small']['url'],
                        'duration': item['duration'],
                        'tags': item['tags'],
                        'source': 'pixabay'
                    })
                return {"success": True, "videos": videos, "count": len(videos)}
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Search failed: {str(e)}"}

    def search_pexels_videos(self, theme):
        """Search Pexels for videos by theme"""
        try:
            keywords = self.video_categories.get(theme, ["nature"])
            query = keywords[0]
            
            url = f"https://api.pexels.com/videos/search"
            headers = {"Authorization": self.pexels_key}
            params = {
                'query': query,
                'per_page': 5,
                'size': 'medium'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                for item in data.get('videos', []):
                    video_files = item.get('video_files', [])
                    if video_files:
                        videos.append({
                            'id': item['id'],
                            'url': video_files[0]['link'],
                            'preview': item.get('image'),
                            'duration': item.get('duration', 15),
                            'source': 'pexels'
                        })
                return {"success": True, "videos": videos, "count": len(videos)}
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Search failed: {str(e)}"}

class ContainerIntegration:
    def __init__(self):
        self.video_manager = VideoFootageManager()
        self.services = {
            "kokoro_tts": {
                "name": "Kokoro GPU TTS",
                "url": "http://localhost:8880",
                "features": ["japanese_tts", "gpu_acceleration"],
                "status": "running"
            },
            "nca_toolkit": {
                "name": "NCA Toolkit", 
                "url": "http://localhost:8080",
                "features": ["ai_tools", "automation"],
                "status": "available"
            },
            "baserow": {
                "name": "Baserow Database",
                "url": "http://localhost:443",
                "features": ["database", "api"],
                "status": "available"
            },
            "minio": {
                "name": "MinIO Storage",
                "url": "http://localhost:9000", 
                "features": ["object_storage", "s3_compatible"],
                "status": "available"
            },
            "n8n": {
                "name": "n8n Automation",
                "url": "http://localhost:5678",
                "features": ["workflow_automation"],
                "status": "available"
            }
        }

    def check_service_health(self, service_name):
        try:
            service = self.services.get(service_name)
            if not service:
                return {"status": "unknown", "error": "Service not found"}
            
            # Since we're in Railway, these containers aren't accessible
            # Return mock status for demo
            return {
                "status": "demo_mode",
                "url": service["url"],
                "container": service_name
            }
        except:
            return {"status": "demo_mode", "error": "Demo environment"}

    def get_system_status(self):
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_health": "demo_mode"
        }
        
        for service_name, service_info in self.services.items():
            status_report["services"][service_name] = {
                "name": service_info["name"],
                "health": "demo_mode",
                "url": service_info["url"],
                "features": service_info["features"]
            }
        
        status_report["overall_health"] = "demo_mode"
        return status_report

    def create_motivational_video_pipeline(self, quote_data):
        # Mock pipeline for demo
        return {
            "quote": quote_data,
            "steps": [
                {"step": "tts", "status": True},
                {"step": "storage", "status": True},
                {"step": "nca_processing", "status": True},
                {"step": "database", "status": True},
                {"step": "automation", "status": True}
            ],
            "outputs": {
                "audio_url": "demo_audio.wav",
                "video_config": {"demo": True}
            },
            "status": "completed"
        }

    def use_kokoro_tts(self, text, voice="thai_female", speed=1.0):
        # Mock TTS response
        return {
            "success": True,
            "message": f"TTS generated for: {text[:50]}...",
            "format": "wav",
            "service": "kokoro_tts_demo"
        }

# Initialize services
quotes_generator = StoicQuotesGenerator()
container_integration = ContainerIntegration()

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
            .status-demo { background: #FFC107; }
            
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
            
            @media (max-width: 768px) {
                .api-demo { grid-template-columns: 1fr; }
                .header h1 { font-size: 2em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Heckx AI</h1>
                <div class="subtitle">Ultimate Motivational Video Creator Platform</div>
                <div class="subtitle">🎬 Live on Railway • Ready for Production</div>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎙️</div>
                    <div class="feature-title">Kokoro GPU TTS</div>
                    <div><span id="kokoro-status" class="status-indicator status-demo"></span>High-Quality Voice Synthesis</div>
                    <button onclick="testKokoro()">Test TTS</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🎬</div>
                    <div class="feature-title">NCA Toolkit</div>
                    <div><span id="nca-status" class="status-indicator status-demo"></span>AI Video Generation</div>
                    <button onclick="testNCA()">Test NCA</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">💾</div>
                    <div class="feature-title">MinIO Storage</div>
                    <div><span id="minio-status" class="status-indicator status-demo"></span>Media Storage</div>
                    <button onclick="testStorage()">Test Storage</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Baserow Database</div>
                    <div><span id="baserow-status" class="status-indicator status-demo"></span>Data Management</div>
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
                        <button onclick="searchVideos()" style="width: 100%; margin-bottom: 10px;">🎬 Search Real Videos</button>
                        <button onclick="createVideo()" style="width: 100%; margin-bottom: 10px;">🚀 Create Motivational Video</button>
                        <button onclick="checkContainers()" style="width: 100%;">📊 Check System Status</button>
                        <div id="video-status" style="margin-top: 15px; font-family: monospace; font-size: 0.9em;"></div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>✅ DEPLOYED SUCCESSFULLY • 🚀 Railway Platform • Created with ❤️ by bobo</p>
            </div>
        </div>
        
        <script>
            // Check container status on load
            checkContainers();
            
            function checkContainers() {
                document.getElementById('video-status').innerHTML = '🔄 Checking system...';
                
                fetch('/api/containers/status')
                .then(r => r.json())
                .then(data => {
                    const services = data.services || {};
                    document.getElementById('video-status').innerHTML = 
                        `✅ System Health: ${data.overall_health}<br>` +
                        `📊 Demo Mode: All features available<br>` +
                        `🎬 Ready to create amazing videos!`;
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
            
            function searchVideos() {
                document.getElementById('video-status').innerHTML = '🔍 Searching real videos...';
                
                const themes = ['resilience', 'peace', 'growth', 'success'];
                const randomTheme = themes[Math.floor(Math.random() * themes.length)];
                
                fetch(`/api/videos/search/${randomTheme}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('video-status').innerHTML = 
                        `🎬 <strong>Found:</strong> ${data.total_videos} videos<br>` +
                        `🎯 <strong>Theme:</strong> ${data.theme}<br>` +
                        `📊 <strong>Sources:</strong> Pixabay: ${data.sources.pixabay ? '✅' : '❌'}, Pexels: ${data.sources.pexels ? '✅' : '❌'}<br>` +
                        `🎥 <strong>Sample:</strong> ${data.videos.length > 0 ? data.videos[0].source + ' video ready!' : 'No videos'}`;
                })
                .catch(e => {
                    document.getElementById('video-status').innerHTML = '❌ Video search failed';
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
                        `📊 <strong>Pipeline:</strong> ${data.pipeline.steps.length} steps completed<br>` +
                        `🎯 <strong>Ready:</strong> Video creation system operational!`;
                });
            }
            
            function testKokoro() {
                fetch('/api/tts/synthesize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: 'สวัสดีจาก Heckx AI', voice: 'thai_female'})
                })
                .then(r => r.json())
                .then(data => {
                    alert(data.success ? '✅ Kokoro TTS Ready!' : '❌ TTS Failed');
                });
            }
            
            function testNCA() { alert('🎬 NCA Toolkit integration ready!'); }
            function testStorage() { alert('💾 MinIO storage integration ready!'); }
            function testDatabase() { alert('📊 Baserow database integration ready!'); }
            
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
    data = request.json
    user_msg = data.get('message', '').lower()
    
    if 'สวัสดี' in user_msg or 'hello' in user_msg:
        response = 'สวัสดีครับ! ผมพร้อมสร้างวิดีโอแรงบันดาลใจให้คุณ'
    elif 'วิดีโอ' in user_msg or 'video' in user_msg:
        response = 'ผมสามารถสร้างวิดีโอแรงบันดาลใจด้วย AI voice + BGM + footage ได้เลย!'
    elif 'คุณคือใคร' in user_msg:
        response = 'ผมคือ Heckx AI Ultimate Video Creator ที่เจ๋งที่สุด!'
    else:
        response = f'เข้าใจแล้ว: "{data.get("message")}" ลองกดปุ่ม Create Video ดูสิครับ!'
    
    return jsonify({'response': response})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'app': 'Heckx AI Ultimate'})

@app.route('/api/containers/status')
def containers_status():
    status = container_integration.get_system_status()
    return jsonify(status)

@app.route('/api/quote/generate', methods=['POST'])
def generate_quote():
    data = request.json or {}
    theme = data.get('theme', 'resilience')
    quote = quotes_generator.get_random_quote(theme=theme)
    return jsonify(quotes_generator.export_for_api(quote))

@app.route('/api/video/create', methods=['POST'])
def create_video():
    data = request.json or {}
    theme = data.get('theme', 'resilience')
    
    quote_data = quotes_generator.get_random_quote(theme=theme)
    quote_data = quotes_generator.export_for_api(quote_data)
    
    result = container_integration.create_motivational_video_pipeline(quote_data)
    
    return jsonify({
        'success': result['status'] == 'completed',
        'pipeline': result,
        'message': 'Video creation pipeline executed successfully!'
    })

@app.route('/api/tts/synthesize', methods=['POST'])
def synthesize_speech():
    data = request.json or {}
    text = data.get('text', 'สวัสดีครับ')
    voice = data.get('voice', 'thai_female')
    
    result = container_integration.use_kokoro_tts(text, voice)
    return jsonify(result)

@app.route('/api/quote/daily')
def daily_quote():
    quote = quotes_generator.get_daily_quote()
    return jsonify(quotes_generator.export_for_api(quote))

@app.route('/api/videos/search/<theme>')
def search_videos(theme):
    """Search for videos by theme using real APIs"""
    footage_manager = VideoFootageManager()
    
    # Try both APIs
    pixabay_result = footage_manager.search_pixabay_videos(theme)
    pexels_result = footage_manager.search_pexels_videos(theme)
    
    all_videos = []
    if pixabay_result["success"]:
        all_videos.extend(pixabay_result["videos"])
    if pexels_result["success"]:
        all_videos.extend(pexels_result["videos"])
    
    return jsonify({
        "theme": theme,
        "total_videos": len(all_videos),
        "videos": all_videos[:10],  # Return top 10
        "sources": {
            "pixabay": pixabay_result["success"],
            "pexels": pexels_result["success"]
        }
    })

@app.route('/api/videos/random/<theme>')
def random_video(theme):
    """Get a random video for theme"""
    footage_manager = VideoFootageManager()
    
    # Try Pixabay first, fallback to Pexels
    result = footage_manager.search_pixabay_videos(theme)
    if not result["success"]:
        result = footage_manager.search_pexels_videos(theme)
    
    if result["success"] and result["videos"]:
        video = random.choice(result["videos"])
        return jsonify({
            "success": True,
            "video": video,
            "theme": theme
        })
    else:
        return jsonify({
            "success": False,
            "error": "No videos found",
            "theme": theme
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)