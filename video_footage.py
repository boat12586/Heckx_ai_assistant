#!/usr/bin/env python3
"""
Video Footage Integration for Heckx AI
Stock videos from Pixabay and Pexels
"""

import requests
import json
import os
from urllib.parse import urlencode

class VideoFootageManager:
    def __init__(self):
        # Free stock video APIs
        self.pixabay_key = os.environ.get('PIXABAY_API_KEY', 'demo-key')
        self.pexels_key = os.environ.get('PEXELS_API_KEY', 'demo-key')
        
        # Curated footage collections
        self.stoic_footage = {
            "mountain": [
                "https://cdn.pixabay.com/vimeo/447607/mountains-4470.mp4",
                "https://cdn.pixabay.com/vimeo/456789/peak-4567.mp4"
            ],
            "ocean": [
                "https://cdn.pixabay.com/vimeo/334455/ocean-3344.mp4", 
                "https://cdn.pixabay.com/vimeo/556677/waves-5566.mp4"
            ],
            "forest": [
                "https://cdn.pixabay.com/vimeo/778899/forest-7788.mp4",
                "https://cdn.pixabay.com/vimeo/990011/trees-9900.mp4"
            ],
            "sunset": [
                "https://cdn.pixabay.com/vimeo/112233/sunset-1122.mp4",
                "https://cdn.pixabay.com/vimeo/445566/golden-hour-4455.mp4"
            ],
            "sky": [
                "https://cdn.pixabay.com/vimeo/667788/clouds-6677.mp4",
                "https://cdn.pixabay.com/vimeo/889900/timelapse-8899.mp4"
            ]
        }
        
        # Video specifications for each mood
        self.video_specs = {
            "resilience": {
                "keywords": ["mountain", "storm", "waves", "strong"],
                "mood": "dramatic",
                "duration": "10-20",
                "style": "cinematic"
            },
            "peace": {
                "keywords": ["sunset", "calm", "meditation", "zen"],
                "mood": "peaceful", 
                "duration": "15-25",
                "style": "serene"
            },
            "growth": {
                "keywords": ["forest", "plant", "sunrise", "growth"],
                "mood": "inspiring",
                "duration": "12-18",
                "style": "uplifting"
            }
        }

    def search_pixabay_videos(self, query, category="nature"):
        """Search Pixabay for videos"""
        try:
            params = {
                'key': self.pixabay_key,
                'q': query,
                'video_type': 'film',
                'category': category,
                'min_duration': 10,
                'per_page': 10,
                'safesearch': 'true'
            }
            
            url = f"https://pixabay.com/api/videos/?{urlencode(params)}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.format_pixabay_results(data)
            else:
                return self.get_fallback_footage(query)
                
        except Exception as e:
            print(f"Pixabay search error: {e}")
            return self.get_fallback_footage(query)

    def search_pexels_videos(self, query):
        """Search Pexels for videos"""
        try:
            headers = {
                'Authorization': self.pexels_key
            }
            params = {
                'query': query,
                'per_page': 10,
                'size': 'medium'
            }
            
            url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.format_pexels_results(data)
            else:
                return self.get_fallback_footage(query)
                
        except Exception as e:
            print(f"Pexels search error: {e}")
            return self.get_fallback_footage(query)

    def format_pixabay_results(self, data):
        """Format Pixabay API results"""
        videos = []
        for item in data.get('hits', []):
            videos.append({
                'id': item['id'],
                'url': item['videos']['medium']['url'],
                'thumbnail': item['userImageURL'],
                'duration': item['duration'],
                'tags': item['tags'],
                'source': 'pixabay',
                'quality': 'medium'
            })
        return videos

    def format_pexels_results(self, data):
        """Format Pexels API results"""
        videos = []
        for item in data.get('videos', []):
            video_files = item.get('video_files', [])
            if video_files:
                videos.append({
                    'id': item['id'],
                    'url': video_files[0]['link'],
                    'thumbnail': item.get('image'),
                    'duration': item.get('duration', 15),
                    'tags': [],
                    'source': 'pexels',
                    'quality': video_files[0]['quality']
                })
        return videos

    def get_fallback_footage(self, theme):
        """Get curated footage when APIs fail"""
        footage_urls = self.stoic_footage.get(theme, self.stoic_footage["mountain"])
        
        fallback_videos = []
        for i, url in enumerate(footage_urls[:3]):
            fallback_videos.append({
                'id': f'fallback_{theme}_{i}',
                'url': url,
                'thumbnail': url.replace('.mp4', '_thumb.jpg'),
                'duration': 15,
                'tags': [theme, 'stoic', 'motivational'],
                'source': 'curated',
                'quality': 'hd'
            })
        
        return fallback_videos

    def get_footage_for_quote(self, quote_theme, quote_background):
        """Get the best footage for a specific quote"""
        # Try multiple sources
        sources = [
            lambda: self.search_pixabay_videos(quote_background, "nature"),
            lambda: self.search_pexels_videos(quote_background),
            lambda: self.get_fallback_footage(quote_background)
        ]
        
        for source_func in sources:
            try:
                videos = source_func()
                if videos:
                    return {
                        'selected': videos[0],  # Best match
                        'alternatives': videos[1:4],  # Alternative options
                        'theme': quote_theme,
                        'background': quote_background
                    }
            except:
                continue
        
        # Ultimate fallback
        return {
            'selected': {
                'id': 'default_mountain',
                'url': 'https://cdn.pixabay.com/vimeo/447607/mountains-4470.mp4',
                'thumbnail': 'https://cdn.pixabay.com/photo/2023/12/08/mountain-thumbnail.jpg',
                'duration': 15,
                'tags': ['mountain', 'nature'],
                'source': 'default',
                'quality': 'hd'
            },
            'alternatives': [],
            'theme': quote_theme,
            'background': quote_background
        }

    def download_video(self, video_url, output_path):
        """Download video for processing"""
        try:
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False

    def get_video_info(self, video_path):
        """Get video metadata using ffprobe"""
        try:
            import subprocess
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return None
        except:
            return None

# Test the footage manager
if __name__ == "__main__":
    manager = VideoFootageManager()
    
    # Test getting footage for a quote
    footage = manager.get_footage_for_quote("resilience", "mountain")
    print("Selected footage:", footage['selected'])
    print("Alternatives:", len(footage['alternatives']))