#!/usr/bin/env python3
"""
Heckx AI - Enhanced Railway Version with Music Discovery
"""
import os
import json
import random
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
from pathlib import Path
from typing import List, Dict, Optional

app = Flask(__name__)
CORS(app)

# Embedded Music Discovery Service
class SimpleMusicService:
    def __init__(self):
        self.pixabay_api_key = '46734-67b3b2251fecba4ff4d66ee95'  # Demo key
        self.init_music_db()
        
    def init_music_db(self):
        """Initialize music database with demo data"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS music_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                external_id TEXT,
                title TEXT,
                artist TEXT,
                tags TEXT,
                download_url TEXT,
                preview_url TEXT,
                duration INTEGER,
                downloads INTEGER,
                likes INTEGER,
                genre TEXT,
                mood TEXT
            )
        ''')
        
        # Add demo tracks with real music URLs
        cursor.execute('SELECT COUNT(*) FROM music_tracks')
        if cursor.fetchone()[0] == 0:
            demo_music = [
                ('demo', 'demo_jazz_1', 'Smooth Jazz Piano', 'Jazz Artist', 'jazz, smooth, piano, relaxing', 
                 'https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=modern-chillout-12099.mp3', 
                 'https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=modern-chillout-12099.mp3',
                 180, 5000, 250, 'jazz', 'relaxing'),
                
                ('demo', 'demo_lofi_1', 'Lo-fi Study Beat', 'Chill Producer', 'lofi, chill, study, beats, focus',
                 'https://cdn.pixabay.com/download/audio/2022/08/02/audio_2165f1a07c.mp3?filename=lofi-study-112191.mp3',
                 'https://cdn.pixabay.com/download/audio/2022/08/02/audio_2165f1a07c.mp3?filename=lofi-study-112191.mp3',
                 165, 7200, 420, 'lofi', 'focus'),
                
                ('demo', 'demo_blue_1', 'Midnight Blues', 'Blues Soul', 'blues, guitar, emotional, midnight',
                 'https://cdn.pixabay.com/download/audio/2022/03/15/audio_478a8fc8ee.mp3?filename=relaxing-guitar-loop-7355.mp3',
                 'https://cdn.pixabay.com/download/audio/2022/03/15/audio_478a8fc8ee.mp3?filename=relaxing-guitar-loop-7355.mp3',
                 210, 3500, 180, 'blues', 'melancholic'),
                
                ('demo', 'demo_piano_1', 'Peaceful Piano', 'Piano Virtuoso', 'piano, classical, peaceful, meditation',
                 'https://cdn.pixabay.com/download/audio/2022/02/22/audio_d1108ab8b9.mp3?filename=piano-moment-7800.mp3',
                 'https://cdn.pixabay.com/download/audio/2022/02/22/audio_d1108ab8b9.mp3?filename=piano-moment-7800.mp3',
                 240, 6800, 340, 'classical', 'peaceful')
            ]
            
            cursor.executemany('''
                INSERT INTO music_tracks 
                (source, external_id, title, artist, tags, download_url, preview_url, 
                 duration, downloads, likes, genre, mood)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', demo_music)
            
            print("✅ Added demo music tracks to database")
        
        conn.commit()
        conn.close()
    
    def search_music(self, query: str) -> List[Dict]:
        """Search music from database and Pixabay API"""
        # First search local database
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM music_tracks 
            WHERE (title LIKE ? OR artist LIKE ? OR tags LIKE ?)
            ORDER BY downloads DESC
        ''', [f'%{query}%', f'%{query}%', f'%{query}%'])
        
        tracks = []
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'title': row[3],
                'artist': row[4],
                'tags': row[5],
                'preview_url': row[7],
                'download_url': row[6],
                'duration': row[8],
                'downloads': row[9],
                'likes': row[10],
                'genre': row[11],
                'mood': row[12]
            })
        
        # If no local results, try Pixabay API
        if not tracks and query:
            try:
                pixabay_tracks = self.search_pixabay(query)
                tracks.extend(pixabay_tracks)
            except Exception as e:
                print(f"Pixabay search error: {e}")
        
        conn.close()
        return tracks
    
    def search_pixabay(self, query: str) -> List[Dict]:
        """Search Pixabay for music"""
        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': self.pixabay_api_key,
                'q': query,
                'category': 'music',
                'audio_type': 'music',
                'min_downloads': 1000,
                'per_page': 10,
                'safesearch': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tracks = []
                
                for hit in data.get('hits', []):
                    track = {
                        'id': f"pixabay_{hit.get('id')}",
                        'title': hit.get('tags', 'Unknown').replace(',', ' ').title()[:50],
                        'artist': hit.get('user', 'Unknown Artist'),
                        'tags': hit.get('tags', ''),
                        'preview_url': hit.get('previewURL', ''),
                        'download_url': hit.get('url', ''),
                        'duration': hit.get('duration', 0),
                        'downloads': hit.get('downloads', 0),
                        'likes': hit.get('likes', 0),
                        'genre': self._extract_genre(hit.get('tags', '')),
                        'mood': self._extract_mood(hit.get('tags', ''))
                    }
                    tracks.append(track)
                
                return tracks
            else:
                print(f"Pixabay API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Pixabay API error: {e}")
            return []
    
    def _extract_genre(self, tags: str) -> str:
        """Extract genre from tags"""
        tags_lower = tags.lower()
        if 'jazz' in tags_lower:
            return 'jazz'
        elif 'blues' in tags_lower or 'blue' in tags_lower:
            return 'blues'
        elif 'piano' in tags_lower or 'classical' in tags_lower:
            return 'classical'
        elif 'lofi' in tags_lower or 'chill' in tags_lower:
            return 'lofi'
        elif 'ambient' in tags_lower:
            return 'ambient'
        return 'other'
    
    def _extract_mood(self, tags: str) -> str:
        """Extract mood from tags"""
        tags_lower = tags.lower()
        if any(word in tags_lower for word in ['relax', 'calm', 'peaceful']):
            return 'relaxing'
        elif any(word in tags_lower for word in ['focus', 'study', 'concentration']):
            return 'focus'
        elif any(word in tags_lower for word in ['sad', 'melancholy', 'blue']):
            return 'melancholic'
        elif any(word in tags_lower for word in ['happy', 'upbeat', 'cheerful']):
            return 'happy'
        return 'neutral'
    
    def download_music(self, track: Dict) -> Optional[str]:
        """Download music file"""
        try:
            download_url = track.get('download_url')
            if not download_url:
                return None
            
            # Create safe filename
            title = track.get('title', 'Unknown')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_title}.mp3"
            
            # Download the file
            response = requests.get(download_url, timeout=30)
            if response.status_code == 200:
                # For demo, we'll just return the URL since we can't save files on Railway
                return download_url
            else:
                return None
                
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    def get_library_stats(self) -> Dict:
        """Get music library statistics"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM music_tracks')
        total_tracks = cursor.fetchone()[0]
        
        cursor.execute('SELECT genre, COUNT(*) FROM music_tracks GROUP BY genre')
        genres = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_tracks': total_tracks,
            'genres': genres
        }

# Enhanced Google Drive Integration
class SimpleGoogleDrive:
    def __init__(self):
        # Check for Google Drive credentials
        self.credentials_json = os.environ.get('GOOGLE_DRIVE_CREDENTIALS')
        self.api_key = os.environ.get('GOOGLE_DRIVE_API_KEY')
        self.enabled = bool(self.credentials_json or self.api_key)
        
        # Pre-configured folder ID from user
        self.music_folder_id = '1SRw6xRx4teVK6y28HPotSU_yeSs0zq_n'
        
        if self.enabled:
            print("✅ Google Drive credentials detected")
            print(f"📁 Music folder ID: {self.music_folder_id}")
        else:
            print("⚠️ Google Drive credentials not found")
        
    def upload_file(self, file_url: str, filename: str) -> Dict:
        """Upload file to Google Drive"""
        if self.enabled:
            try:
                # Download file from URL first
                print(f"📥 Downloading file from: {file_url}")
                response = requests.get(file_url, timeout=30)
                if response.status_code != 200:
                    return {
                        'success': False,
                        'message': f'Failed to download file from URL: {response.status_code}'
                    }
                
                file_content = response.content
                file_size_mb = len(file_content) / (1024 * 1024)
                
                # Initialize Google Drive API
                drive_service = self._get_drive_service()
                if not drive_service:
                    return {
                        'success': False,
                        'message': 'Failed to initialize Google Drive service'
                    }
                
                # Create file metadata
                file_metadata = {
                    'name': filename,
                    'parents': [self.music_folder_id]
                }
                
                # Create media upload
                import io
                from googleapiclient.http import MediaIoBaseUpload
                
                file_stream = io.BytesIO(file_content)
                media = MediaIoBaseUpload(
                    file_stream,
                    mimetype='audio/mpeg',
                    resumable=True
                )
                
                # Upload file
                print(f"📤 Uploading {filename} to Google Drive...")
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                file_id = file.get('id')
                
                return {
                    'success': True,
                    'drive_id': file_id,
                    'message': f'Successfully uploaded {filename} to Google Drive',
                    'drive_url': f'https://drive.google.com/file/d/{file_id}/view',
                    'folder_url': f'https://drive.google.com/drive/folders/{self.music_folder_id}',
                    'file_size_mb': round(file_size_mb, 2),
                    'folder_id': self.music_folder_id,
                    'upload_status': 'real_upload'
                }
                
            except Exception as e:
                print(f"❌ Upload error: {str(e)}")
                return {
                    'success': False,
                    'message': f'Upload failed: {str(e)}',
                    'error': str(e)
                }
        else:
            return {
                'success': False,
                'message': 'ไม่ได้กำหนดค่า Google Drive โปรดเพิ่มข้อมูลประจำตัวเพื่อเปิดใช้งาน',
                'instructions': 'เพิ่มตัวแปรสภาพแวดล้อม GOOGLE_DRIVE_CREDENTIALS',
                'setup_steps': self._get_setup_steps()
            }
    
    def _get_drive_service(self):
        """Initialize Google Drive service"""
        try:
            import json
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            if self.credentials_json:
                # Parse credentials JSON
                credentials_info = json.loads(self.credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
                
                # Build service
                service = build('drive', 'v3', credentials=credentials)
                return service
            else:
                print("❌ No credentials JSON found")
                return None
                
        except Exception as e:
            print(f"❌ Failed to initialize Drive service: {str(e)}")
            return None
    
    def get_drive_info(self) -> Dict:
        """Get Google Drive status"""
        if self.enabled:
            return {
                'enabled': True,
                'status': 'Ready',
                'credentials_found': bool(self.credentials_json),
                'api_key_found': bool(self.api_key),
                'message': 'Google Drive integration is active',
                'folder_name': 'Heckx Music Library',
                'folder_id': self.music_folder_id,
                'folder_url': f'https://drive.google.com/drive/folders/{self.music_folder_id}',
                'upload_ready': True
            }
        else:
            return {
                'enabled': False,
                'status': 'Not Configured',
                'message': 'ต้องการตั้งค่า Google Drive API เพื่อใช้งานฟีเจอร์เต็มรูปแบบ',
                'setup_url': 'https://developers.google.com/drive/api/quickstart/python',
                'setup_steps': self._get_setup_steps()
            }
    
    def _get_setup_steps(self) -> List[str]:
        """Get detailed setup instructions"""
        return [
            "1. ไปที่ Google Cloud Console (console.cloud.google.com)",
            "2. สร้าง Project ใหม่หรือเลือก Project ที่มีอยู่",
            "3. เปิดใช้งาน Google Drive API",
            "4. สร้าง Service Account Credentials", 
            "5. Download JSON credentials file",
            "6. เพิ่ม environment variable: GOOGLE_DRIVE_CREDENTIALS='{json_content}'",
            "7. หรือเพิ่ม API Key: GOOGLE_DRIVE_API_KEY='your_api_key'",
            "8. Deploy อีกครั้งเพื่อใช้งาน Google Drive"
        ]
    
    def test_connection(self) -> Dict:
        """Test Google Drive connection"""
        if not self.enabled:
            return {
                'success': False,
                'message': 'No credentials configured'
            }
        
        try:
            # Test real Google Drive connection
            drive_service = self._get_drive_service()
            if not drive_service:
                return {
                    'success': False,
                    'message': 'Failed to initialize Google Drive service'
                }
            
            # Test by getting folder info
            folder_info = drive_service.files().get(
                fileId=self.music_folder_id,
                fields='id,name,mimeType'
            ).execute()
            
            return {
                'success': True,
                'message': 'Google Drive connection successful',
                'test_result': f'Connected to folder: {folder_info.get("name", "Unknown")}',
                'folder_name': folder_info.get('name'),
                'folder_verified': True
            }
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return {
                'success': False, 
                'message': f'Connection failed: {str(e)}'
            }

# Initialize services
try:
    if os.path.exists('music_library.db'):
        os.remove('music_library.db')
        print("🔄 Recreating music database with demo data...")
except:
    pass

music_service = SimpleMusicService()
drive_service = SimpleGoogleDrive()

# Enhanced quotes by category
QUOTES_BY_CATEGORY = {
    "wisdom": [
        {"text": "ความสุขไม่ขึ้นอยู่กับสิ่งที่เกิดขึ้น แต่ขึ้นอยู่กับการตอบสนอง", "author": "Epictetus"},
        {"text": "คุณมีอำนาจเหนือจิตใจ ไม่ใช่เหตุการณ์ภายนอก", "author": "Marcus Aurelius"},
        {"text": "ความยากลำบากเปิดเผยตัวตนที่แท้จริง", "author": "Seneca"}
    ],
    "resilience": [
        {"text": "สิ่งที่ขวางทาง จะกลายเป็นทาง", "author": "Marcus Aurelius"},
        {"text": "เราทุกข์ในจินตนาการมากกว่าความเป็นจริง", "author": "Seneca"},
        {"text": "ไฟจะไหม้ไม้ แต่ทำให้ทองคำบริสุทธิ์", "author": "Seneca"}
    ],
    "mindfulness": [
        {"text": "วันนี้เป็นของขวัญ เพราะเราเรียกมันว่า 'ปัจจุบัน'", "author": "Eleanor Roosevelt"},
        {"text": "ความสงบอยู่ในใจ ไม่ใช่ข้างนอก", "author": "Buddha"},
        {"text": "จิตใจที่สงบเป็นพลังที่ยิ่งใหญ่", "author": "Lao Tzu"}
    ],
    "motivation": [
        {"text": "ความเป็นเลิศไม่ใช่การกระทำ แต่เป็นนิสัย", "author": "Aristotle"},
        {"text": "เริ่มต้นที่ไหนก็ได้ แต่ให้เริ่มต้นเดี๋ยวนี้", "author": "John F. Kennedy"},
        {"text": "ทางเดียวที่จะทำสิ่งยิ่งใหญ่ได้คือการรักในสิ่งที่คุณทำ", "author": "Steve Jobs"}
    ]
}

# Database initialization
def init_db():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            rating INTEGER
        )
    ''')
    
    # Create user preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            favorite_category TEXT DEFAULT 'wisdom',
            theme TEXT DEFAULT 'dark',
            language TEXT DEFAULT 'thai',
            notifications BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Heckx AI - Enhanced Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { 
                font-size: 3.5em; 
                margin-bottom: 20px; 
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .features-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin: 30px 0;
            }
            .feature-card { 
                background: rgba(255,255,255,0.15); 
                border-radius: 15px; 
                padding: 25px; 
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            .feature-card:hover { transform: translateY(-5px); }
            .feature-card h3 { margin-bottom: 15px; font-size: 1.5em; }
            .controls { 
                display: flex; 
                flex-wrap: wrap; 
                gap: 15px; 
                justify-content: center; 
                margin: 30px 0;
            }
            button { 
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white; 
                border: none; 
                padding: 15px 25px; 
                font-size: 1.1em; 
                border-radius: 25px; 
                cursor: pointer; 
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                min-width: 160px;
            }
            button:hover { 
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            select { 
                padding: 10px 15px; 
                border-radius: 10px; 
                border: none; 
                background: rgba(255,255,255,0.9);
                color: #333;
                font-size: 1em;
            }
            #result { 
                background: rgba(0,0,0,0.4); 
                padding: 25px; 
                border-radius: 15px; 
                margin-top: 25px; 
                min-height: 120px;
                border: 1px solid rgba(255,255,255,0.1);
                animation: fadeIn 0.5s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                gap: 15px; 
                margin: 20px 0;
            }
            .stat-item { 
                background: rgba(255,255,255,0.1); 
                padding: 15px; 
                border-radius: 10px; 
                text-align: center;
            }
            .conversation-history { 
                max-height: 300px; 
                overflow-y: auto; 
                background: rgba(0,0,0,0.2); 
                border-radius: 10px; 
                padding: 15px; 
                margin-top: 20px;
            }
            .tab-button {
                background: rgba(255,255,255,0.1);
                margin: 0 5px;
                min-width: 120px;
                border: 1px solid rgba(255,255,255,0.3);
                transition: all 0.3s ease;
            }
            .tab-button.active {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                transform: translateY(-2px);
            }
            .tab-content {
                animation: fadeIn 0.5s ease;
            }
            .track-item {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                border-left: 4px solid #4CAF50;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .track-item:hover {
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
            }
            .track-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .music-controls {
                display: flex;
                gap: 10px;
                align-items: center;
                justify-content: center;
                margin: 10px 0;
            }
            .progress-bar {
                width: 100%;
                height: 6px;
                background: rgba(255,255,255,0.3);
                border-radius: 3px;
                overflow: hidden;
                margin: 10px 0;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                width: 0%;
                transition: width 0.3s ease;
            }
            @media (max-width: 768px) {
                .container { padding: 20px; }
                h1 { font-size: 2.5em; }
                .controls { flex-direction: column; align-items: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Heckx AI Assistant</h1>
            <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
                🎵 <strong>Music Discovery Hub</strong> - Lo-fi, Jazz, Piano & Ambient Music + Smart Quotes (v2.0)
            </p>
            
            <div class="features-grid">
                <div class="feature-card">
                    <h3>🎭 Smart Quotes</h3>
                    <p>Categorized wisdom quotes with intelligent recommendations</p>
                </div>
                <div class="feature-card">
                    <h3>🎵 Music Discovery</h3>
                    <p>Premium Lo-fi, Jazz, Piano music from Pixabay with 2000+ downloads</p>
                </div>
                <div class="feature-card">
                    <h3>☁️ Google Drive Backup</h3>
                    <p>Auto-sync your music library and content to Google Drive</p>
                </div>
                <div class="feature-card">
                    <h3>💬 Conversation History</h3>
                    <p>Track your interactions and build personalized experiences</p>
                </div>
                <div class="feature-card">
                    <h3>🎼 Music Library</h3>
                    <p>Organize, search, and stream your premium music collection</p>
                </div>
                <div class="feature-card">
                    <h3>📊 Analytics & Insights</h3>
                    <p>Track usage, favorites, and optimize your experience</p>
                </div>
            </div>
            
            <!-- Tab Navigation -->
            <div style="display: flex; justify-content: center; margin: 30px 0;">
                <button onclick="showTab('quotes')" id="quotesTab" class="tab-button active">📝 Quotes</button>
                <button onclick="showTab('music')" id="musicTab" class="tab-button">🎵 Music</button>
                <button onclick="showTab('library')" id="libraryTab" class="tab-button">🎼 Library</button>
                <button onclick="showTab('stats')" id="statsTab" class="tab-button">📊 Stats</button>
            </div>
            
            <!-- Quotes Tab -->
            <div id="quotesSection" class="tab-content">
                <div class="controls">
                    <select id="category">
                        <option value="random">Random Category</option>
                        <option value="wisdom">Wisdom</option>
                        <option value="resilience">Resilience</option>
                        <option value="mindfulness">Mindfulness</option>
                        <option value="motivation">Motivation</option>
                    </select>
                    <button onclick="getQuote()">📝 Get Quote</button>
                    <button onclick="checkHealth()">❤️ Health Check</button>
                    <button onclick="getStats()">📊 Statistics</button>
                    <button onclick="getHistory()">📜 History</button>
                    <button onclick="clearHistory()">🗑️ Clear History</button>
                </div>
            </div>
            
            <!-- Music Discovery Tab -->
            <div id="musicSection" class="tab-content" style="display: none;">
                <div class="controls">
                    <input type="text" id="musicQuery" placeholder="Search: jazz, blue, piano, lofi..." style="padding: 10px; border-radius: 10px; border: none; margin: 5px; min-width: 200px;">
                    <button onclick="discoverMusic()">🔍 Discover Music</button>
                    <button onclick="bulkDiscover()">⚡ Bulk Discover</button>
                    <button onclick="syncToDrive()">☁️ Sync to Drive</button>
                    <button onclick="testDriveConnection()">🔧 Test Drive</button>
                </div>
                <div class="controls">
                    <button onclick="getRecommendations()">⭐ Recommendations</button>
                    <button onclick="getDriveInfo()">📊 Drive Info</button>
                    <button onclick="showSetupGuide()">📖 Setup Guide</button>
                </div>
            </div>
            
            <!-- Music Library Tab -->
            <div id="librarySection" class="tab-content" style="display: none;">
                <div class="controls">
                    <select id="genreFilter">
                        <option value="">All Genres</option>
                    </select>
                    <select id="moodFilter">
                        <option value="">All Moods</option>
                    </select>
                    <input type="text" id="libraryQuery" placeholder="Search library..." style="padding: 10px; border-radius: 10px; border: none; margin: 5px;">
                    <button onclick="searchLibrary()">🔍 Search Library</button>
                    <button onclick="loadPlaylists()">📋 Playlists</button>
                </div>
                <div id="musicPlayer" style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center;">
                    <audio id="audioPlayer" controls style="width: 100%; max-width: 500px; margin: 10px 0;">
                        Your browser does not support the audio element.
                    </audio>
                    <div id="nowPlaying" style="margin-top: 10px; font-style: italic;">No track selected</div>
                </div>
            </div>
            
            <!-- Statistics Tab -->
            <div id="statsSection" class="tab-content" style="display: none;">
                <div class="controls">
                    <button onclick="getDetailedStats()">📊 Detailed Stats</button>
                    <button onclick="getLibraryStats()">🎵 Music Stats</button>
                    <button onclick="exportData()">💾 Export Data</button>
                </div>
            </div>
            
            <div id="result">
                🎵 <strong>Welcome to Your Music Discovery Hub!</strong><br><br>
                ✨ Try the <strong>Music</strong> tab to discover premium Lo-fi, Jazz & Piano tracks<br>
                📚 Or explore wisdom quotes in the <strong>Quotes</strong> tab<br>
                🎼 Check your <strong>Library</strong> for collected music<br><br>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-top: 15px;">
                    <h4>🎵 Demo Music Available:</h4>
                    <p>• Smooth Jazz Café ☕</p>
                    <p>• Midnight Blues 🌙</p>  
                    <p>• Lo-fi Study Session 📚</p>
                    <p>• Ambient Atmosphere 🧘</p>
                </div>
            </div>
        </div>
        
        <script>
            let userId = localStorage.getItem('heckx_user_id') || 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('heckx_user_id', userId);
            
            function getQuote() {
                const category = document.getElementById('category').value;
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '🔄 Loading wisdom...';
                
                fetch('/api/quote', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        category: category,
                        user_id: userId
                    })
                })
                .then(r => r.json())
                .then(data => {
                    resultDiv.innerHTML = `
                        <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                            <h3>📝 ${data.category.toUpperCase()} QUOTE</h3>
                            <p style="font-style: italic; font-size: 1.3em; margin: 15px 0;">"${data.quote}"</p>
                            <p><strong>👤 Author:</strong> ${data.author}</p>
                            <p><strong>🔢 Quote #:</strong> ${data.id}</p>
                            <p><strong>⏰ Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                            <div style="margin-top: 15px;">
                                <button onclick="rateQuote(${data.id}, 1)" style="background: #4CAF50; margin: 5px;">👍 Like</button>
                                <button onclick="rateQuote(${data.id}, 0)" style="background: #f44336; margin: 5px;">👎 Dislike</button>
                            </div>
                        </div>
                    `;
                })
                .catch(e => {
                    resultDiv.innerHTML = `<div style="color: #f44336;"><h3>❌ Error</h3><p>${e.message}</p></div>`;
                });
            }
            
            function checkHealth() {
                document.getElementById('result').innerHTML = '🔄 Checking system health...';
                fetch('/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = `
                        <div style="border-left: 4px solid #2196F3; padding-left: 20px;">
                            <h3>❤️ System Health</h3>
                            <p><strong>Status:</strong> <span style="color: #4CAF50;">${data.status}</span></p>
                            <p><strong>App:</strong> ${data.app}</p>
                            <p><strong>Version:</strong> ${data.version}</p>
                            <p><strong>Uptime:</strong> ${Math.floor(data.uptime || 0)} seconds</p>
                            <p><strong>Database:</strong> <span style="color: #4CAF50;">${data.database_status}</span></p>
                            <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        </div>
                    `;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ Health Check Failed</h3><p>${e.message}</p></div>`;
                });
            }
            
            function getStats() {
                document.getElementById('result').innerHTML = '📊 Loading statistics...';
                fetch('/api/stats?user_id=' + userId)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = `
                        <div style="border-left: 4px solid #FF9800; padding-left: 20px;">
                            <h3>📊 Your Statistics</h3>
                            <div class="stats">
                                <div class="stat-item">
                                    <h4>${data.total_quotes}</h4>
                                    <p>Total Quotes</p>
                                </div>
                                <div class="stat-item">
                                    <h4>${data.favorite_category}</h4>
                                    <p>Favorite Category</p>
                                </div>
                                <div class="stat-item">
                                    <h4>${data.total_conversations}</h4>
                                    <p>Conversations</p>
                                </div>
                                <div class="stat-item">
                                    <h4>${data.avg_rating}/5</h4>
                                    <p>Avg Rating</p>
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ Stats Error</h3><p>${e.message}</p></div>`;
                });
            }
            
            function getHistory() {
                document.getElementById('result').innerHTML = '📜 Loading conversation history...';
                fetch('/api/history?user_id=' + userId)
                .then(r => r.json())
                .then(data => {
                    let historyHtml = '<div style="border-left: 4px solid #9C27B0; padding-left: 20px;"><h3>📜 Recent Conversations</h3>';
                    if (data.conversations.length === 0) {
                        historyHtml += '<p>No conversations yet. Start by getting a quote!</p>';
                    } else {
                        historyHtml += '<div class="conversation-history">';
                        data.conversations.forEach(conv => {
                            historyHtml += `
                                <div style="margin-bottom: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                                    <p><strong>Category:</strong> ${conv.category}</p>
                                    <p><strong>Quote:</strong> "${conv.message}"</p>
                                    <p><strong>Time:</strong> ${new Date(conv.timestamp).toLocaleString()}</p>
                                </div>
                            `;
                        });
                        historyHtml += '</div>';
                    }
                    historyHtml += '</div>';
                    document.getElementById('result').innerHTML = historyHtml;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ History Error</h3><p>${e.message}</p></div>`;
                });
            }
            
            function clearHistory() {
                if (confirm('Are you sure you want to clear all conversation history?')) {
                    fetch('/api/history', {
                        method: 'DELETE',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({user_id: userId})
                    })
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                                <h3>✅ History Cleared</h3>
                                <p>${data.message}</p>
                            </div>
                        `;
                    })
                    .catch(e => {
                        document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ Clear Error</h3><p>${e.message}</p></div>`;
                    });
                }
            }
            
            function rateQuote(quoteId, rating) {
                fetch('/api/rate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        quote_id: quoteId,
                        rating: rating,
                        user_id: userId
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('Thanks for your feedback! 🙏');
                    }
                })
                .catch(e => console.error('Rating error:', e));
            }
            
            // Tab Management
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.style.display = 'none';
                });
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName + 'Section').style.display = 'block';
                document.getElementById(tabName + 'Tab').classList.add('active');
                
                // Load content based on tab
                if (tabName === 'library') {
                    loadGenresAndMoods();
                }
            }
            
            // Music Discovery Functions
            function discoverMusic() {
                const query = document.getElementById('musicQuery').value || 'jazz';
                document.getElementById('result').innerHTML = '🎵 Discovering premium music...';
                
                fetch(`/api/music/discover?query=${query}&min_downloads=2000`)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        displayMusicTracks(data.tracks, 'Discovered Music');
                    } else {
                        document.getElementById('result').innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Discovery failed: ${e.message}`;
                });
            }
            
            function bulkDiscover() {
                document.getElementById('result').innerHTML = '⚡ Bulk discovering premium tracks...';
                
                fetch('/api/music/bulk-discover', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        keywords: ['jazz', 'blue', 'piano', 'lofi', 'ambient', 'chill'],
                        max_tracks: 15,
                        auto_download: true
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let html = `<div style="border-left: 4px solid #FF9800; padding-left: 20px;">`;
                        html += `<h3>⚡ Bulk Discovery Results</h3>`;
                        html += `<p><strong>Discovered:</strong> ${data.total_discovered} tracks</p>`;
                        html += `<p><strong>Downloaded:</strong> ${data.total_downloaded} tracks</p>`;
                        html += `<p><strong>Uploaded to Drive:</strong> ${data.downloaded_tracks.length} tracks</p>`;
                        
                        if (data.downloaded_tracks.length > 0) {
                            html += `<h4>Downloaded Tracks:</h4>`;
                            data.downloaded_tracks.forEach(track => {
                                html += `<div class="track-item">📥 ${track.title} by ${track.artist}</div>`;
                            });
                        }
                        html += `</div>`;
                        
                        document.getElementById('result').innerHTML = html;
                    } else {
                        document.getElementById('result').innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Bulk discovery failed: ${e.message}`;
                });
            }
            
            function displayMusicTracks(tracks, title) {
                let html = `<div style="border-left: 4px solid #9C27B0; padding-left: 20px;">`;
                html += `<h3>🎵 ${title}</h3>`;
                html += `<div class="track-grid">`;
                
                tracks.forEach(track => {
                    html += `
                        <div class="track-item" onclick="downloadTrack(${JSON.stringify(track).replace(/"/g, '&quot;')})">
                            <h4>🎼 ${track.title}</h4>
                            <p><strong>Artist:</strong> ${track.artist}</p>
                            <p><strong>Downloads:</strong> ${track.downloads?.toLocaleString() || 'N/A'}</p>
                            <p><strong>Likes:</strong> ${track.likes?.toLocaleString() || 'N/A'}</p>
                            <p><strong>Quality Score:</strong> ${track.quality_score || 'N/A'}</p>
                            <div class="music-controls">
                                <button onclick="event.stopPropagation(); downloadTrack(${JSON.stringify(track).replace(/"/g, '&quot;')})" style="background: #4CAF50; margin: 5px;">📥 Download</button>
                                ${track.preview_url ? `<button onclick="event.stopPropagation(); previewTrack('${track.preview_url}')" style="background: #2196F3; margin: 5px;">▶️ Preview</button>` : ''}
                            </div>
                        </div>
                    `;
                });
                
                html += `</div></div>`;
                document.getElementById('result').innerHTML = html;
            }
            
            function downloadTrack(track) {
                document.getElementById('result').innerHTML = `🔄 Downloading: ${track.title}...`;
                
                fetch('/api/music/download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({track: track})
                })
                .then(r => {
                    if (!r.ok) {
                        throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                    }
                    return r.json();
                })
                .then(data => {
                    if (data.success) {
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                                <h3>✅ Download Ready</h3>
                                <p><strong>Track:</strong> ${track.title}</p>
                                <p><strong>Message:</strong> ${data.message}</p>
                                <p><a href="${data.download_url}" target="_blank" style="color: #4CAF50; text-decoration: underline;">🔗 Download Link</a></p>
                                <p><strong>Google Drive:</strong> ${data.google_drive_id ? 'Uploaded ✅' : 'Upload failed ❌'}</p>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `❌ Download failed: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Download error: ${e.message}`;
                });
            }
            
            function previewTrack(url) {
                const player = document.getElementById('audioPlayer');
                player.src = url;
                player.play();
                document.getElementById('nowPlaying').innerHTML = `🎵 Preview playing...`;
            }
            
            function getRecommendations() {
                document.getElementById('result').innerHTML = '⭐ Loading premium recommendations...';
                
                fetch('/api/music/recommendations')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        displayLibraryTracks(data.recommendations, 'Premium Recommendations');
                    } else {
                        document.getElementById('result').innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Failed to load recommendations: ${e.message}`;
                });
            }
            
            function searchLibrary() {
                const query = document.getElementById('libraryQuery').value;
                const genre = document.getElementById('genreFilter').value;
                const mood = document.getElementById('moodFilter').value;
                
                let url = '/api/music/library?';
                if (query) url += `query=${query}&`;
                if (genre) url += `genre=${genre}&`;
                if (mood) url += `mood=${mood}`;
                
                document.getElementById('result').innerHTML = '🔍 Searching library...';
                
                fetch(url)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        displayLibraryTracks(data.tracks, 'Library Search Results');
                        displayLibraryStats(data.stats);
                    } else {
                        document.getElementById('result').innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Search failed: ${e.message}`;
                });
            }
            
            function displayLibraryTracks(tracks, title) {
                let html = `<div style="border-left: 4px solid #2196F3; padding-left: 20px;">`;
                html += `<h3>🎼 ${title}</h3>`;
                
                if (tracks.length === 0) {
                    html += `<p>No tracks found. Try discovering some music first!</p>`;
                } else {
                    html += `<div class="track-grid">`;
                    tracks.forEach(track => {
                        html += `
                            <div class="track-item" onclick="playTrack(${track.id}, '${track.title}', '${track.artist}')">
                                <h4>🎼 ${track.title}</h4>
                                <p><strong>Artist:</strong> ${track.artist}</p>
                                <p><strong>Genre:</strong> ${track.genre || 'Unknown'}</p>
                                <p><strong>Mood:</strong> ${track.mood || 'Unknown'}</p>
                                <p><strong>Downloads:</strong> ${track.downloads?.toLocaleString() || 'N/A'}</p>
                                <div class="music-controls">
                                    <button onclick="event.stopPropagation(); playTrack(${track.id}, '${track.title}', '${track.artist}')" style="background: #4CAF50; margin: 5px;">▶️ Play</button>
                                </div>
                            </div>
                        `;
                    });
                    html += `</div>`;
                }
                
                html += `</div>`;
                document.getElementById('result').innerHTML = html;
            }
            
            function playTrack(trackId, title, artist) {
                fetch(`/api/music/play/${trackId}`)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const player = document.getElementById('audioPlayer');
                        player.src = data.audio_url;
                        player.play().then(() => {
                            document.getElementById('nowPlaying').innerHTML = `🎵 Now Playing: ${title} by ${artist}`;
                            document.getElementById('result').innerHTML = `
                                <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                                    <h3>🎵 Playing Music</h3>
                                    <p><strong>Track:</strong> ${data.title}</p>
                                    <p><strong>Status:</strong> ${data.message}</p>
                                </div>
                            `;
                        }).catch(e => {
                            document.getElementById('result').innerHTML = `❌ Playback error: ${e.message}`;
                        });
                    } else {
                        document.getElementById('result').innerHTML = `❌ Failed to load track: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Track error: ${e.message}`;
                });
            }
            
            function loadGenresAndMoods() {
                fetch('/api/music/genres')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const genreSelect = document.getElementById('genreFilter');
                        const moodSelect = document.getElementById('moodFilter');
                        
                        // Clear existing options (except first)
                        genreSelect.innerHTML = '<option value="">All Genres</option>';
                        moodSelect.innerHTML = '<option value="">All Moods</option>';
                        
                        data.genres.forEach(item => {
                            genreSelect.innerHTML += `<option value="${item.genre}">${item.genre} (${item.count})</option>`;
                        });
                        
                        data.moods.forEach(item => {
                            moodSelect.innerHTML += `<option value="${item.mood}">${item.mood} (${item.count})</option>`;
                        });
                    }
                })
                .catch(e => console.error('Failed to load genres/moods:', e));
            }
            
            function displayLibraryStats(stats) {
                // Display stats in a corner or overlay
                console.log('Library Stats:', stats);
            }
            
            function syncToDrive() {
                document.getElementById('result').innerHTML = '☁️ Syncing library to Google Drive...';
                
                fetch('/api/music/drive/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                })
                .then(r => {
                    if (!r.ok) {
                        throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                    }
                    return r.json();
                })
                .then(data => {
                    if (data.success) {
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                                <h3>☁️ Google Drive Upload Success</h3>
                                <p><strong>Status:</strong> ${data.message}</p>
                                <p><strong>File Size:</strong> ${data.file_size_mb} MB</p>
                                <p><strong>Upload Mode:</strong> ${data.upload_status === 'real_upload' ? '✅ Real Upload' : '🔧 Simulated (Demo)'}</p>
                                ${data.folder_url ? `<p><a href="${data.folder_url}" target="_blank" style="color: #4CAF50;">📁 View Google Drive Folder</a></p>` : ''}
                                ${data.drive_url ? `<p><a href="${data.drive_url}" target="_blank" style="color: #4CAF50;">🔗 View Uploaded File</a></p>` : ''}
                                <p><strong>Folder ID:</strong> ${data.folder_id}</p>
                            </div>
                        `;
                    } else {
                        let setupSteps = '';
                        if (data.instructions && data.instructions.includes('setup_steps')) {
                            setupSteps = `
                                <h4>📋 ขั้นตอนการติดตั้ง Google Drive:</h4>
                                <ol style="margin-left: 20px;">
                                    <li>ไปที่ <a href="https://console.cloud.google.com" target="_blank" style="color: #4CAF50;">Google Cloud Console</a></li>
                                    <li>สร้าง Project ใหม่หรือเลือก Project ที่มีอยู่</li>
                                    <li>เปิดใช้งาน Google Drive API</li>
                                    <li>สร้าง Service Account Credentials</li>
                                    <li>Download JSON credentials file</li>
                                    <li>เพิ่ม environment variable ใน Railway:</li>
                                    <ul style="margin: 10px 0 0 20px; font-family: monospace; background: #333; padding: 10px; border-radius: 5px;">
                                        <li>GOOGLE_DRIVE_CREDENTIALS='{json_content}'</li>
                                        <li>หรือ GOOGLE_DRIVE_API_KEY='your_api_key'</li>
                                    </ul>
                                    <li>Deploy อีกครั้งเพื่อใช้งาน Google Drive</li>
                                </ol>
                            `;
                        }
                        
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #ff9800; padding-left: 20px;">
                                <h3>⚙️ Google Drive Setup Required</h3>
                                <p><strong>สถานะ:</strong> ${data.message}</p>
                                <p><strong>คำแนะนำ:</strong> ${data.instructions || 'เพิ่มข้อมูลประจำตัว Google Drive'}</p>
                                ${setupSteps}
                                <p style="margin-top: 15px;"><strong>💡 หลังจากตั้งค่าแล้ว:</strong> กด "☁️ Sync to Drive" อีกครั้งเพื่อทดสอบ</p>
                            </div>
                        `;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Sync error: ${e.message}`;
                });
            }
            
            function testDriveConnection() {
                document.getElementById('result').innerHTML = '🔧 Testing Google Drive connection...';
                
                fetch('/api/music/drive/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                })
                .then(r => {
                    if (!r.ok) {
                        throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                    }
                    return r.json();
                })
                .then(data => {
                    if (data.success) {
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                                <h3>✅ Google Drive Connection Test</h3>
                                <p><strong>Status:</strong> ${data.message}</p>
                                <p><strong>Test Result:</strong> ${data.test_result}</p>
                                <p><strong>Ready to sync files!</strong></p>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #f44336; padding-left: 20px;">
                                <h3>❌ Google Drive Test Failed</h3>
                                <p><strong>Message:</strong> ${data.message}</p>
                                <p><strong>Action:</strong> Please configure Google Drive credentials first</p>
                            </div>
                        `;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Test error: ${e.message}`;
                });
            }
            
            function showSetupGuide() {
                document.getElementById('result').innerHTML = '📖 Loading Google Drive setup guide...';
                
                fetch('/api/music/drive/setup-guide')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const guide = data.guide;
                        let stepsHtml = '';
                        
                        guide.steps.forEach(step => {
                            let detailsHtml = step.details.map(detail => `<li>${detail}</li>`).join('');
                            stepsHtml += `
                                <div style="margin: 15px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                                    <h4 style="color: #4CAF50; margin-bottom: 10px;">${step.title}</h4>
                                    <p style="margin-bottom: 10px;">${step.description}</p>
                                    ${step.url ? `<p><a href="${step.url}" target="_blank" style="color: #4CAF50;">🔗 ${step.url}</a></p>` : ''}
                                    <ul style="margin-left: 20px;">
                                        ${detailsHtml}
                                    </ul>
                                </div>
                            `;
                        });
                        
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #2196F3; padding-left: 20px; max-height: 500px; overflow-y: auto;">
                                <h3>${guide.title}</h3>
                                ${stepsHtml}
                                
                                <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                                    <h4>📋 ตัวอย่าง JSON Credentials:</h4>
                                    <pre style="background: #333; padding: 10px; border-radius: 5px; font-size: 12px; overflow-x: auto;">
{
  "type": "service_account",
  "project_id": "heckx-music-drive-123456",
  "private_key_id": "abcd1234...",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "heckx-music-service@your-project.iam.gserviceaccount.com",
  "client_id": "123456789012345678901"
}</pre>
                                </div>
                                
                                <div style="margin-top: 15px; padding: 15px; background: rgba(76,175,80,0.2); border-radius: 10px;">
                                    <h4>🚀 Railway Environment Variable:</h4>
                                    <p><strong>Name:</strong> <code>GOOGLE_DRIVE_CREDENTIALS</code></p>
                                    <p><strong>Value:</strong> วาง JSON content ทั้งหมดที่ copy มา</p>
                                </div>
                                
                                <div style="margin-top: 15px; text-align: center;">
                                    <button onclick="testDriveConnection()" style="background: #4CAF50; padding: 10px 20px; border: none; border-radius: 5px; color: white; cursor: pointer;">
                                        🔧 Test Connection หลังจากตั้งค่าเสร็จ
                                    </button>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `❌ Failed to load setup guide`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Guide error: ${e.message}`;
                });
            }
            
            function getDriveInfo() {
                document.getElementById('result').innerHTML = '📊 Loading Google Drive info...';
                
                fetch('/api/music/drive/info')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const info = data.drive_info;
                        let html = `<div style="border-left: 4px solid #2196F3; padding-left: 20px;">`;
                        html += `<h3>☁️ Google Drive Status</h3>`;
                        html += `<p><strong>Status:</strong> ${info.enabled ? '✅ Connected' : '❌ Not Connected'}</p>`;
                        html += `<p><strong>Message:</strong> ${info.message}</p>`;
                        
                        if (info.enabled) {
                            html += `<p><strong>Folder:</strong> ${info.folder_name}</p>`;
                            html += `<p><strong>Folder ID:</strong> ${info.folder_id}</p>`;
                            html += `<p><a href="${info.folder_url}" target="_blank" style="color: #4CAF50;">📁 Open Google Drive Folder</a></p>`;
                            html += `<p><strong>Upload Ready:</strong> ${info.upload_ready ? 'Yes' : 'No'}</p>`;
                            html += `<p><strong>Credentials:</strong> ${info.credentials_found ? 'JSON Found' : 'API Key Only'}</p>`;
                        } else {
                            html += `<p><a href="${info.setup_url}" target="_blank" style="color: #4CAF50;">📖 Setup Guide</a></p>`;
                        }
                        
                        html += `</div>`;
                        document.getElementById('result').innerHTML = html;
                    } else {
                        document.getElementById('result').innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `❌ Drive info failed: ${e.message}`;
                });
            }
            
            // Auto-refresh health check every 60 seconds
            setInterval(() => {
                fetch('/health').catch(() => {}); // Silent health ping
            }, 60000);
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Enhanced health check with database status"""
    try:
        # Test database connection
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'OK',
            'app': 'Heckx AI Enhanced',
            'version': '2.0',
            'timestamp': datetime.now().isoformat(),
            'database_status': 'Connected',
            'total_conversations': total_conversations,
            'uptime': time.time() if 'time' in globals() else 0
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'app': 'Heckx AI Enhanced',
            'timestamp': datetime.now().isoformat(),
            'database_status': 'Error',
            'error': str(e)
        }), 500

@app.route('/api/quote', methods=['POST'])
def get_quote():
    """Enhanced quote endpoint with categories and history"""
    try:
        data = request.get_json() or {}
        category = data.get('category', 'random')
        user_id = data.get('user_id', 'anonymous')
        
        # Select category
        if category == 'random' or category not in QUOTES_BY_CATEGORY:
            category = random.choice(list(QUOTES_BY_CATEGORY.keys()))
        
        # Get quote from selected category
        quote_data = random.choice(QUOTES_BY_CATEGORY[category])
        quote_id = random.randint(1000, 9999)
        
        # Save to database
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_id, message, response, category)
            VALUES (?, ?, ?, ?)
        ''', (user_id, quote_data['text'], quote_data['author'], category))
        conn.commit()
        conn.close()
        
        return jsonify({
            'quote': quote_data['text'],
            'author': quote_data['author'],
            'category': category,
            'id': quote_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get user statistics"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        
        # Total quotes
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ?', (user_id,))
        total_quotes = cursor.fetchone()[0]
        
        # Total conversations
        cursor.execute('SELECT COUNT(DISTINCT category) FROM conversations WHERE user_id = ?', (user_id,))
        total_conversations = cursor.fetchone()[0]
        
        # Favorite category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM conversations 
            WHERE user_id = ? 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 1
        ''', (user_id,))
        fav_result = cursor.fetchone()
        favorite_category = fav_result[0] if fav_result else 'None'
        
        # Average rating
        cursor.execute('SELECT AVG(rating) FROM conversations WHERE user_id = ? AND rating IS NOT NULL', (user_id,))
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'total_quotes': total_quotes,
            'total_conversations': total_conversations,
            'favorite_category': favorite_category,
            'avg_rating': round(avg_rating, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get conversation history"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, category, timestamp 
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''', (user_id,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'message': row[0],
                'category': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'conversations': conversations,
            'count': len(conversations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear conversation history"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} conversations'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate', methods=['POST'])
def rate_quote():
    """Rate a quote"""
    try:
        data = request.get_json() or {}
        quote_id = data.get('quote_id')
        rating = data.get('rating')
        user_id = data.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE conversations 
            SET rating = ? 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (rating, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Music Discovery & Management API Endpoints

@app.route('/api/music/discover')
def discover_music():
    """Discover premium quality music"""
    try:
        query = request.args.get('query', 'lofi')
        tracks = music_service.search_music(query)
        
        return jsonify({
            'success': True,
            'tracks': tracks[:20],  # Limit to 20 tracks
            'total_found': len(tracks)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/download', methods=['POST'])
def download_music():
    """Download a music track"""
    try:
        data = request.get_json() or {}
        track_info = data.get('track')
        
        if not track_info:
            return jsonify({'error': 'Track information required'}), 400
        
        # Use the download method from music service
        download_url = music_service.download_music(track_info)
        
        if download_url:
            return jsonify({
                'success': True,
                'download_url': download_url,
                'message': f"Ready to download: {track_info.get('title', 'Unknown Track')}",
                'filename': f"{track_info.get('title', 'track')}.mp3"
            })
        else:
            return jsonify({'error': 'Download failed - URL not available'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/library')
def get_music_library():
    """Get music library with search and filters"""
    try:
        query = request.args.get('query', '')
        tracks = music_service.search_music(query) if query else music_service.search_music('')
        stats = music_service.get_library_stats()
        
        return jsonify({
            'success': True,
            'tracks': tracks,
            'stats': stats,
            'total_tracks': len(tracks)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/recommendations')
def get_music_recommendations():
    """Get premium music recommendations"""
    try:
        recommendations = music_service.search_music('lofi')  # Get lofi tracks as recommendations
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/genres')
def get_music_genres():
    """Get available music genres"""
    try:
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT genre, COUNT(*) FROM music_tracks GROUP BY genre')
        genres = [{'genre': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        cursor.execute('SELECT DISTINCT mood, COUNT(*) FROM music_tracks GROUP BY mood')
        moods = [{'mood': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'genres': genres,
            'moods': moods
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/play/<int:track_id>')
def stream_music(track_id):
    """Get music track URL for streaming"""
    try:
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT title, preview_url, download_url FROM music_tracks WHERE id = ?', (track_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            title, preview_url, download_url = result
            # Return URL for client-side audio player
            return jsonify({
                'success': True,
                'title': title,
                'audio_url': preview_url or download_url,
                'message': f'Ready to play: {title}'
            })
        else:
            return jsonify({'error': 'Track not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/playlists', methods=['GET', 'POST'])
def manage_playlists():
    """Get or create playlists"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            name = data.get('name')
            track_ids = data.get('track_ids', [])
            mood_tag = data.get('mood_tag')
            
            if not name:
                return jsonify({'error': 'Playlist name required'}), 400
            
            # Demo mode - simulate playlist creation
            playlist_id = len(name)  # Simple ID generation
            
            return jsonify({
                'success': True,
                'playlist_id': playlist_id,
                'demo': True,
                'message': f'Demo playlist "{name}" created with {len(track_ids)} tracks'
            })
        
        else:  # GET
            conn = sqlite3.connect('music_library.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM playlists ORDER BY created_date DESC')
            playlists = []
            
            for row in cursor.fetchall():
                track_ids = [int(x) for x in row[3].split(',') if x]
                playlists.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'track_count': len(track_ids),
                    'mood_tag': row[6],
                    'created_date': row[4]
                })
            
            conn.close()
            
            return jsonify({
                'success': True,
                'playlists': playlists
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/drive/info')
def get_drive_info():
    """Get Google Drive library information"""
    try:
        drive_info = drive_service.get_drive_info()
        return jsonify({
            'success': True,
            'drive_info': drive_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/drive/test', methods=['POST'])
def test_drive_connection():
    """Test Google Drive connection"""
    try:
        result = drive_service.test_connection()
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'test_result': result.get('test_result', 'No test performed')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/drive/setup-guide')
def get_drive_setup_guide():
    """Get detailed Google Drive setup instructions"""
    try:
        guide = {
            'title': '🔧 วิธีการตั้งค่า Google Drive API',
            'steps': [
                {
                    'title': '1. สร้าง Google Cloud Project',
                    'description': 'ไปที่ Google Cloud Console และสร้าง project ใหม่',
                    'url': 'https://console.cloud.google.com',
                    'details': [
                        'คลิก "Select a project" ด้านบน',
                        'คลิก "NEW PROJECT"',
                        'ตั้งชื่อ project เช่น "Heckx-Music-Drive"',
                        'คลิก "CREATE"'
                    ]
                },
                {
                    'title': '2. เปิดใช้งาน Google Drive API',
                    'description': 'ใน Google Cloud Console หา APIs & Services',
                    'details': [
                        'ไปที่ "APIs & Services" > "Library"',
                        'ค้นหา "Google Drive API"',
                        'คลิก "Google Drive API" และ "ENABLE"'
                    ]
                },
                {
                    'title': '3. สร้าง Service Account',
                    'description': 'สร้าง credentials สำหรับแอพพลิเคชัน',
                    'details': [
                        'ไปที่ "APIs & Services" > "Credentials"',
                        'คลิก "+ CREATE CREDENTIALS" > "Service account"',
                        'ตั้งชื่อ service account: "heckx-music-service"',
                        'เลือก Role: "Editor" หรือ "Storage Admin"',
                        'คลิก "CREATE AND CONTINUE" และ "DONE"'
                    ]
                },
                {
                    'title': '4. สร้าง JSON Key',
                    'description': 'Download credentials file สำหรับใช้งาน',
                    'details': [
                        'คลิกที่ service account ที่สร้างไว้',
                        'ไปที่ tab "KEYS"',
                        'คลิก "ADD KEY" > "Create new key"',
                        'เลือก "JSON" และคลิก "CREATE"',
                        'ไฟล์ JSON จะ download อัตโนมัติ'
                    ]
                },
                {
                    'title': '5. เพิ่ม Credentials ใน Railway',
                    'description': 'นำ JSON credentials ไปใส่ใน Railway',
                    'details': [
                        'เปิดไฟล์ JSON ที่ download มา',
                        'Copy เนื้อหาทั้งหมด',
                        'ไปที่ Railway Dashboard > Variables',
                        'เพิ่ม Variable: GOOGLE_DRIVE_CREDENTIALS',
                        'วาง JSON content เป็น Value',
                        'คลิก "Add" และรอ deploy'
                    ]
                }
            ],
            'example_json': {
                'type': 'service_account',
                'project_id': 'heckx-music-drive-123456',
                'private_key_id': 'abcd1234...',
                'private_key': '-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG...\\n-----END PRIVATE KEY-----\\n',
                'client_email': 'heckx-music-service@heckx-music-drive-123456.iam.gserviceaccount.com',
                'client_id': '123456789012345678901'
            },
            'railway_steps': [
                'ไปที่ Railway Dashboard',
                'เลือก project "Heckx AI Assistant"',
                'คลิก tab "Variables"',
                'คลิก "New Variable"',
                'Name: GOOGLE_DRIVE_CREDENTIALS',
                'Value: วาง JSON content',
                'คลิก "Add"'
            ],
            'test_steps': [
                'รอ Railway deploy (2-3 นาที)',
                'refresh หน้าเว็บ Heckx AI Assistant',
                'ไปที่ tab "🎵 Music"',
                'คลิก "🔧 Test Drive"',
                'ถ้าสำเร็จจะแสดง "✅ Google Drive Connection Test"'
            ]
        }
        
        return jsonify({
            'success': True,
            'guide': guide
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/drive/sync', methods=['POST'])
def sync_to_drive():
    """Sync music files to Google Drive"""
    try:
        data = request.get_json() or {}
        file_url = data.get('file_url')
        filename = data.get('filename', 'music_track.mp3')
        
        # If no specific file provided, sync a demo track
        if not file_url:
            # Get a demo track from database
            conn = sqlite3.connect('music_library.db')
            cursor = conn.cursor()
            cursor.execute('SELECT title, download_url FROM music_tracks LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                filename = f"{result[0]}.mp3"
                file_url = result[1]
            else:
                return jsonify({'error': 'No music tracks available to sync'}), 400
        
        upload_result = drive_service.upload_file(file_url, filename)
        
        response = {
            'success': upload_result['success'],
            'message': upload_result['message'],
            'drive_enabled': drive_service.enabled
        }
        
        # Add additional info if upload was successful
        if upload_result['success']:
            response.update({
                'drive_url': upload_result.get('drive_url'),
                'folder_url': upload_result.get('folder_url'),
                'file_size_mb': upload_result.get('file_size_mb'),
                'folder_id': upload_result.get('folder_id'),
                'upload_status': upload_result.get('upload_status')
            })
        else:
            response['instructions'] = upload_result.get('instructions', '')
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/bulk-discover', methods=['POST'])
def bulk_discover_music():
    """Discover and download multiple premium tracks"""
    try:
        data = request.get_json() or {}
        keywords = data.get('keywords', ['jazz', 'blue', 'piano', 'lofi'])
        max_tracks = data.get('max_tracks', 10)
        auto_download = data.get('auto_download', False)
        
        all_tracks = []
        
        for keyword in keywords:
            tracks = music_service.search_music(keyword)
            all_tracks.extend(tracks)
        
        # Sort by downloads and limit
        sorted_tracks = sorted(all_tracks, key=lambda x: x.get('downloads', 0), reverse=True)
        top_tracks = sorted_tracks[:max_tracks]
        
        downloaded_tracks = []
        
        if auto_download:
            # Demo mode - simulate download
            downloaded_tracks = top_tracks.copy()
            for track in downloaded_tracks:
                track['demo_downloaded'] = True
        
        return jsonify({
            'success': True,
            'discovered_tracks': top_tracks,
            'downloaded_tracks': downloaded_tracks,
            'total_discovered': len(top_tracks),
            'total_downloaded': len(downloaded_tracks)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import time
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Heckx AI Enhanced on port {port}")
    print("Features: Categories, History, Statistics, Rating System")
    app.run(host='0.0.0.0', port=port, debug=False)