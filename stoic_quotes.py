#!/usr/bin/env python3
"""
Motivational Stoic Quotes Generator for Heckx AI
"""

import random
import json
from datetime import datetime

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
            },
            {
                "quote": "อดีตที่แล้วไป อนาคตที่ยังไม่มา สิ่งเดียวที่เรามีคือปัจจุบันนี้",
                "author": "Marcus Aurelius",
                "theme": "mindfulness",
                "color": "#F39C12",
                "background": "sunrise"
            },
            {
                "quote": "ความแข็งแกร่งที่แท้จริงคือการยอมรับสิ่งที่เปลี่ยนแปลงไม่ได้และเปลี่ยนแปลงสิ่งที่ทำได้",
                "author": "Serenity Prayer (Stoic adaptation)",
                "theme": "acceptance",
                "color": "#3498DB",
                "background": "sky"
            },
            {
                "quote": "การเตรียมใจสำหรับความทุกข์ทำให้ความทุกข์น้อยลง",
                "author": "Seneca",
                "theme": "preparation",
                "color": "#9B59B6",
                "background": "storm"
            },
            {
                "quote": "คุณภาพของชีวิตไม่ได้วัดจากความยาว แต่วัดจากความลึก",
                "author": "Seneca",
                "theme": "quality",
                "color": "#1ABC9C",
                "background": "nature"
            }
        ]
        
        self.english_quotes = [
            {
                "quote": "The happiness of your life depends upon the quality of your thoughts.",
                "author": "Marcus Aurelius",
                "theme": "thoughts",
                "color": "#2C3E50",
                "background": "mountain"
            },
            {
                "quote": "It's not what happens to you, but how you react to it that matters.",
                "author": "Epictetus",
                "theme": "response",
                "color": "#E74C3C",
                "background": "sunset"
            },
            {
                "quote": "The best time to plant a tree was 20 years ago. The second best time is now.",
                "author": "Chinese Proverb (Stoic spirit)",
                "theme": "action",
                "color": "#27AE60",
                "background": "forest"
            }
        ]
        
        self.video_backgrounds = {
            "mountain": "https://pixabay.com/videos/mountains-peaks-snow-landscape/",
            "ocean": "https://pixabay.com/videos/ocean-waves-sea-water-blue/",
            "sunset": "https://pixabay.com/videos/sunset-sky-clouds-evening/",
            "forest": "https://pixabay.com/videos/forest-trees-nature-green/",
            "sunrise": "https://pixabay.com/videos/sunrise-sun-morning-dawn/",
            "sky": "https://pixabay.com/videos/sky-clouds-blue-white-nature/",
            "storm": "https://pixabay.com/videos/storm-clouds-dark-dramatic/",
            "nature": "https://pixabay.com/videos/nature-landscape-scenic-peaceful/"
        }
        
        self.bgm_tracks = {
            "peaceful": "ambient_peace.mp3",
            "inspiring": "uplifting_piano.mp3", 
            "dramatic": "epic_orchestral.mp3",
            "calm": "meditation_bells.mp3",
            "energetic": "motivational_beat.mp3"
        }

    def get_random_quote(self, language="thai", theme=None):
        """Get a random quote with optional theme filter"""
        quotes = self.thai_quotes if language == "thai" else self.english_quotes
        
        if theme:
            quotes = [q for q in quotes if q.get("theme") == theme]
            
        if not quotes:
            quotes = self.thai_quotes  # fallback
            
        return random.choice(quotes)
    
    def get_quote_by_theme(self, theme="resilience", language="thai"):
        """Get quote by specific theme"""
        return self.get_random_quote(language, theme)
    
    def get_daily_quote(self):
        """Get today's quote (deterministic based on date)"""
        today = datetime.now().strftime("%Y-%m-%d")
        random.seed(today)  # Make it consistent for the day
        quote = self.get_random_quote()
        random.seed()  # Reset random seed
        return quote
    
    def create_video_config(self, quote_data):
        """Create complete video configuration"""
        config = {
            "quote": quote_data,
            "video": {
                "background": self.video_backgrounds.get(quote_data["background"], "mountain"),
                "duration": 15,  # seconds
                "resolution": "1920x1080",
                "fps": 30
            },
            "audio": {
                "bgm": self.bgm_tracks.get("peaceful"),
                "volume": 0.3,
                "fade_in": 2,
                "fade_out": 2
            },
            "text": {
                "font": "NotoSansThai-Bold.ttf",
                "size": 48,
                "color": quote_data["color"],
                "shadow": True,
                "animation": "fade_in"
            },
            "effects": {
                "blur_background": True,
                "vignette": True,
                "color_grading": "cinematic"
            }
        }
        return config
    
    def export_for_api(self, quote_data):
        """Export quote data for API response"""
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

# Quick test
if __name__ == "__main__":
    generator = StoicQuotesGenerator()
    
    # Test daily quote
    daily = generator.get_daily_quote()
    print("Daily Quote:", daily["quote"])
    
    # Test video config
    config = generator.create_video_config(daily)
    print("Video Config:", json.dumps(config, indent=2, ensure_ascii=False))