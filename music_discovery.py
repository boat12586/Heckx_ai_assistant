#!/usr/bin/env python3
"""
Music Discovery & Management System
Integrates with Pixabay/Pexels for high-quality music discovery
"""

import os
import json
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
from typing import List, Dict, Optional

class MusicDiscoveryService:
    def __init__(self):
        self.pixabay_api_key = os.environ.get('PIXABAY_API_KEY', 'demo-key')
        self.pexels_api_key = os.environ.get('PEXELS_API_KEY', 'demo-key')
        self.music_dir = Path('./music_library')
        self.music_dir.mkdir(exist_ok=True)
        self.init_music_db()
        
        # Popular search terms for quality music
        self.premium_keywords = [
            'jazz', 'blue', 'piano', 'lofi', 'ambient', 'chill',
            'acoustic', 'smooth', 'relax', 'focus', 'study',
            'meditation', 'calm', 'peaceful', 'instrumental'
        ]
    
    def init_music_db(self):
        """Initialize music database"""
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
                file_path TEXT,
                google_drive_id TEXT,
                download_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                genre TEXT,
                mood TEXT,
                bpm INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                track_ids TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                play_count INTEGER DEFAULT 0,
                mood_tag TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def search_pixabay_music(self, query: str, min_downloads: int = 2000, per_page: int = 20) -> List[Dict]:
        """Search high-quality music from Pixabay"""
        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': self.pixabay_api_key,
                'q': query,
                'category': 'music',
                'audio_type': 'music',
                'min_downloads': min_downloads,
                'per_page': per_page,
                'order': 'popular',
                'safesearch': 'true'
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return self._process_pixabay_results(data.get('hits', []))
            else:
                print(f"Pixabay API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Pixabay search error: {str(e)}")
            return []
    
    def _process_pixabay_results(self, hits: List[Dict]) -> List[Dict]:
        """Process and standardize Pixabay results"""
        processed = []
        for hit in hits:
            track = {
                'source': 'pixabay',
                'external_id': str(hit.get('id')),
                'title': hit.get('tags', 'Unknown').replace(',', ' ').title(),
                'artist': hit.get('user', 'Unknown Artist'),
                'tags': hit.get('tags', ''),
                'download_url': hit.get('url'),
                'preview_url': hit.get('previewURL'),
                'duration': hit.get('duration', 0),
                'downloads': hit.get('downloads', 0),
                'likes': hit.get('likes', 0),
                'file_size': hit.get('size', 0),
                'quality_score': self._calculate_quality_score(hit)
            }
            processed.append(track)
        
        # Sort by quality score (downloads + likes)
        return sorted(processed, key=lambda x: x['quality_score'], reverse=True)
    
    def _calculate_quality_score(self, track_data: Dict) -> int:
        """Calculate quality score based on downloads, likes, and duration"""
        downloads = track_data.get('downloads', 0)
        likes = track_data.get('likes', 0)
        duration = track_data.get('duration', 0)
        
        # Weighted scoring
        score = (downloads * 1.0) + (likes * 2.0) + (duration * 0.1)
        return int(score)
    
    def discover_premium_music(self) -> List[Dict]:
        """Discover premium quality music using curated keywords"""
        all_tracks = []
        
        for keyword in self.premium_keywords:
            print(f"🎵 Searching for '{keyword}' music...")
            tracks = self.search_pixabay_music(keyword, min_downloads=2000, per_page=10)
            all_tracks.extend(tracks)
        
        # Remove duplicates and get top tracks
        unique_tracks = {}
        for track in all_tracks:
            key = f"{track['external_id']}_{track['source']}"
            if key not in unique_tracks or track['quality_score'] > unique_tracks[key]['quality_score']:
                unique_tracks[key] = track
        
        # Return top 50 highest quality tracks
        top_tracks = sorted(unique_tracks.values(), key=lambda x: x['quality_score'], reverse=True)
        return top_tracks[:50]
    
    def download_track(self, track: Dict) -> Optional[str]:
        """Download music track to local storage"""
        try:
            if not track.get('download_url'):
                print(f"No download URL for track: {track.get('title')}")
                return None
            
            # Create safe filename
            safe_title = "".join(c for c in track['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_title}_{track['external_id']}.mp3"
            file_path = self.music_dir / filename
            
            # Download file
            response = requests.get(track['download_url'], timeout=60)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Update track info
                track['file_path'] = str(file_path)
                track['file_size'] = len(response.content)
                
                # Save to database
                self._save_track_to_db(track)
                
                print(f"✅ Downloaded: {track['title']}")
                return str(file_path)
            else:
                print(f"❌ Download failed for: {track['title']}")
                return None
                
        except Exception as e:
            print(f"Download error for {track.get('title', 'Unknown')}: {str(e)}")
            return None
    
    def _save_track_to_db(self, track: Dict):
        """Save track information to database"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO music_tracks 
            (source, external_id, title, artist, tags, download_url, preview_url,
             duration, downloads, likes, file_path, file_size, genre, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            track.get('source'),
            track.get('external_id'),
            track.get('title'),
            track.get('artist'),
            track.get('tags'),
            track.get('download_url'),
            track.get('preview_url'),
            track.get('duration'),
            track.get('downloads'),
            track.get('likes'),
            track.get('file_path'),
            track.get('file_size'),
            self._extract_genre(track.get('tags', '')),
            self._extract_mood(track.get('tags', ''))
        ))
        
        conn.commit()
        conn.close()
    
    def _extract_genre(self, tags: str) -> str:
        """Extract genre from tags"""
        tags_lower = tags.lower()
        genre_keywords = {
            'jazz': ['jazz', 'swing', 'bebop'],
            'blues': ['blues', 'blue'],
            'classical': ['classical', 'piano', 'orchestra'],
            'ambient': ['ambient', 'atmospheric', 'drone'],
            'lofi': ['lofi', 'lo-fi', 'chill', 'study'],
            'electronic': ['electronic', 'synth', 'techno'],
            'folk': ['folk', 'acoustic', 'country'],
            'rock': ['rock', 'guitar', 'electric']
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in tags_lower for keyword in keywords):
                return genre
        return 'unknown'
    
    def _extract_mood(self, tags: str) -> str:
        """Extract mood from tags"""
        tags_lower = tags.lower()
        mood_keywords = {
            'relaxing': ['relax', 'calm', 'peaceful', 'zen', 'meditation'],
            'energetic': ['energy', 'upbeat', 'dynamic', 'active'],
            'focus': ['focus', 'study', 'concentration', 'work'],
            'romantic': ['romantic', 'love', 'intimate', 'soft'],
            'melancholic': ['sad', 'melancholy', 'emotional', 'blue'],
            'happy': ['happy', 'joy', 'cheerful', 'bright'],
            'mysterious': ['mystery', 'dark', 'atmospheric', 'ambient']
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in tags_lower for keyword in keywords):
                return mood
        return 'neutral'
    
    def get_library_stats(self) -> Dict:
        """Get music library statistics"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM music_tracks')
        total_tracks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT genre) FROM music_tracks')
        genres = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(file_size) FROM music_tracks WHERE file_size IS NOT NULL')
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT AVG(duration) FROM music_tracks WHERE duration > 0')
        avg_duration = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT genre, COUNT(*) FROM music_tracks GROUP BY genre ORDER BY COUNT(*) DESC LIMIT 5')
        top_genres = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_tracks': total_tracks,
            'genres': genres,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'avg_duration_seconds': round(avg_duration, 1),
            'top_genres': top_genres
        }
    
    def search_library(self, query: str, genre: str = None, mood: str = None) -> List[Dict]:
        """Search local music library"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        base_query = '''
            SELECT * FROM music_tracks 
            WHERE (title LIKE ? OR artist LIKE ? OR tags LIKE ?)
        '''
        params = [f'%{query}%', f'%{query}%', f'%{query}%']
        
        if genre:
            base_query += ' AND genre = ?'
            params.append(genre)
        
        if mood:
            base_query += ' AND mood = ?'
            params.append(mood)
        
        base_query += ' ORDER BY downloads DESC, likes DESC'
        
        cursor.execute(base_query, params)
        tracks = []
        
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'source': row[1],
                'external_id': row[2],
                'title': row[3],
                'artist': row[4],
                'tags': row[5],
                'file_path': row[11],
                'duration': row[8],
                'downloads': row[9],
                'likes': row[10],
                'genre': row[16],
                'mood': row[17]
            })
        
        conn.close()
        return tracks
    
    def create_playlist(self, name: str, track_ids: List[int], mood_tag: str = None) -> int:
        """Create a new playlist"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        track_ids_str = ','.join(map(str, track_ids))
        
        cursor.execute('''
            INSERT INTO playlists (name, track_ids, mood_tag)
            VALUES (?, ?, ?)
        ''', (name, track_ids_str, mood_tag))
        
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return playlist_id
    
    def get_premium_recommendations(self) -> List[Dict]:
        """Get premium music recommendations based on quality metrics"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        # Get tracks with high downloads and likes
        cursor.execute('''
            SELECT * FROM music_tracks 
            WHERE downloads >= 2000 
            ORDER BY (downloads * 1.0 + likes * 2.0) DESC 
            LIMIT 20
        ''')
        
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'id': row[0],
                'title': row[3],
                'artist': row[4],
                'genre': row[16],
                'mood': row[17],
                'downloads': row[9],
                'likes': row[10],
                'quality_score': row[9] + (row[10] * 2),
                'file_path': row[11]
            })
        
        conn.close()
        return recommendations

def main():
    """Test the music discovery system"""
    music_service = MusicDiscoveryService()
    
    print("🎵 Heckx Music Discovery System")
    print("=" * 50)
    
    # Discover premium music
    print("Discovering premium quality music...")
    premium_tracks = music_service.discover_premium_music()
    
    print(f"Found {len(premium_tracks)} premium tracks")
    
    # Download top 5 tracks for testing
    print("\nDownloading top 5 tracks...")
    for track in premium_tracks[:5]:
        music_service.download_track(track)
    
    # Show library stats
    stats = music_service.get_library_stats()
    print(f"\nLibrary Stats:")
    print(f"Total tracks: {stats['total_tracks']}")
    print(f"Total size: {stats['total_size_mb']} MB")
    print(f"Average duration: {stats['avg_duration_seconds']} seconds")

if __name__ == "__main__":
    main()