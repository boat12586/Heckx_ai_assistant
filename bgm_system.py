#!/usr/bin/env python3
"""
Background Music (BGM) System for Heckx AI Video Creator
"""

import os
import json
import requests
from pathlib import Path

class BGMSystem:
    def __init__(self):
        self.music_library = {
            "peaceful": {
                "tracks": [
                    {
                        "name": "Zen Garden",
                        "url": "https://cdn.pixabay.com/audio/zen-garden-meditation.mp3",
                        "duration": 180,
                        "bpm": 60,
                        "mood": "calm",
                        "instruments": ["piano", "bells", "nature"]
                    },
                    {
                        "name": "Mountain Breeze", 
                        "url": "https://cdn.pixabay.com/audio/mountain-breeze-ambient.mp3",
                        "duration": 210,
                        "bpm": 55,
                        "mood": "serene",
                        "instruments": ["flute", "strings"]
                    }
                ],
                "default_volume": 0.3,
                "fade_duration": 3
            },
            
            "inspiring": {
                "tracks": [
                    {
                        "name": "Rise Up",
                        "url": "https://cdn.pixabay.com/audio/rise-up-motivational.mp3", 
                        "duration": 165,
                        "bpm": 120,
                        "mood": "uplifting",
                        "instruments": ["piano", "strings", "percussion"]
                    },
                    {
                        "name": "New Dawn",
                        "url": "https://cdn.pixabay.com/audio/new-dawn-inspiring.mp3",
                        "duration": 195,
                        "bpm": 100,
                        "mood": "hopeful", 
                        "instruments": ["guitar", "piano", "orchestra"]
                    }
                ],
                "default_volume": 0.4,
                "fade_duration": 2
            },
            
            "dramatic": {
                "tracks": [
                    {
                        "name": "Epic Journey",
                        "url": "https://cdn.pixabay.com/audio/epic-journey-orchestral.mp3",
                        "duration": 240,
                        "bpm": 85,
                        "mood": "powerful",
                        "instruments": ["orchestra", "choir", "drums"]
                    },
                    {
                        "name": "Thunder Storm",
                        "url": "https://cdn.pixabay.com/audio/thunder-storm-dramatic.mp3",
                        "duration": 150,
                        "bpm": 70,
                        "mood": "intense",
                        "instruments": ["strings", "brass", "timpani"]
                    }
                ],
                "default_volume": 0.5,
                "fade_duration": 1.5
            },
            
            "energetic": {
                "tracks": [
                    {
                        "name": "Power Beat",
                        "url": "https://cdn.pixabay.com/audio/power-beat-electronic.mp3",
                        "duration": 200,
                        "bpm": 140,
                        "mood": "energetic",
                        "instruments": ["synth", "drums", "bass"]
                    }
                ],
                "default_volume": 0.45,
                "fade_duration": 2
            }
        }
        
        # Theme to music mapping
        self.theme_music_map = {
            "resilience": "dramatic",
            "control": "inspiring", 
            "response": "peaceful",
            "growth": "inspiring",
            "mindfulness": "peaceful",
            "acceptance": "peaceful",
            "preparation": "dramatic",
            "quality": "inspiring",
            "thoughts": "peaceful",
            "action": "energetic"
        }
        
        # AI-generated music options (if we implement later)
        self.ai_music_providers = {
            "mubert": "https://api.mubert.com/v2/generate",
            "soundraw": "https://api.soundraw.io/generate",
            "boomy": "https://api.boomy.com/create"
        }

    def get_music_for_theme(self, theme, mood_override=None):
        """Get appropriate music for quote theme"""
        music_category = self.theme_music_map.get(theme, "peaceful")
        
        if mood_override:
            music_category = mood_override
            
        category_data = self.music_library.get(music_category, self.music_library["peaceful"])
        tracks = category_data["tracks"]
        
        # Select best track (could add AI selection logic here)
        selected_track = tracks[0] if tracks else None
        
        return {
            "selected": selected_track,
            "alternatives": tracks[1:],
            "category": music_category,
            "volume": category_data["default_volume"],
            "fade_in": category_data["fade_duration"],
            "fade_out": category_data["fade_duration"]
        }

    def create_audio_config(self, quote_theme, video_duration=15):
        """Create complete audio configuration for video"""
        music_config = self.get_music_for_theme(quote_theme)
        
        audio_config = {
            "bgm": music_config["selected"],
            "settings": {
                "volume": music_config["volume"],
                "fade_in": music_config["fade_in"], 
                "fade_out": music_config["fade_out"],
                "loop": video_duration > music_config["selected"]["duration"] if music_config["selected"] else False,
                "start_offset": 0,  # Start from beginning of track
                "end_trim": max(0, music_config["selected"]["duration"] - video_duration) if music_config["selected"] else 0
            },
            "effects": {
                "equalizer": self.get_eq_preset(music_config["category"]),
                "compression": True,
                "normalization": True
            },
            "alternatives": music_config["alternatives"]
        }
        
        return audio_config

    def get_eq_preset(self, category):
        """Get equalizer preset for music category"""
        eq_presets = {
            "peaceful": {
                "low": 0,
                "mid": 2,
                "high": -1,
                "description": "Warm and soft"
            },
            "inspiring": {
                "low": 1,
                "mid": 3,
                "high": 2,
                "description": "Bright and clear"
            },
            "dramatic": {
                "low": 3,
                "mid": 1,
                "high": 0,
                "description": "Deep and powerful"
            },
            "energetic": {
                "low": 2,
                "mid": 2,
                "high": 3,
                "description": "Punchy and crisp"
            }
        }
        
        return eq_presets.get(category, eq_presets["peaceful"])

    def download_track(self, track_url, output_path):
        """Download music track for processing"""
        try:
            response = requests.get(track_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"Track download error: {e}")
            return False

    def process_audio_with_ffmpeg(self, input_path, output_path, config):
        """Process audio with FFmpeg filters"""
        try:
            import subprocess
            
            # Build FFmpeg command with filters
            filters = []
            
            # Volume adjustment
            if config["settings"]["volume"] != 1.0:
                filters.append(f"volume={config['settings']['volume']}")
            
            # Fade effects
            if config["settings"]["fade_in"] > 0:
                filters.append(f"afade=t=in:ss=0:d={config['settings']['fade_in']}")
            
            if config["settings"]["fade_out"] > 0:
                filters.append(f"afade=t=out:ss=10:d={config['settings']['fade_out']}")
            
            # Equalizer
            eq = config["effects"]["equalizer"]
            filters.append(f"equalizer=f=100:width_type=o:width=2:g={eq['low']}")
            filters.append(f"equalizer=f=1000:width_type=o:width=2:g={eq['mid']}")
            filters.append(f"equalizer=f=10000:width_type=o:width=2:g={eq['high']}")
            
            # Compression
            if config["effects"]["compression"]:
                filters.append("acompressor=threshold=0.5:ratio=2:attack=5:release=50")
            
            filter_complex = ",".join(filters)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-af', filter_complex,
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Audio processing error: {e}")
            return False

    def generate_ai_music(self, prompt, duration=15, mood="peaceful"):
        """Generate AI music (placeholder for future AI integration)"""
        # This would integrate with AI music generation APIs
        # For now, return a template response
        return {
            "status": "generated",
            "prompt": prompt,
            "duration": duration,
            "mood": mood,
            "url": "generated_music.mp3",
            "message": "AI music generation coming soon!"
        }

    def create_custom_soundscape(self, base_track, nature_sounds=None, intensity=0.5):
        """Create custom soundscape by mixing tracks"""
        soundscape_config = {
            "base_music": base_track,
            "layers": [],
            "mix_settings": {
                "base_volume": 0.7,
                "layer_volume": 0.3,
                "crossfade": True
            }
        }
        
        # Add nature sounds if specified
        nature_library = {
            "rain": "https://cdn.pixabay.com/audio/rain-gentle.mp3",
            "wind": "https://cdn.pixabay.com/audio/wind-trees.mp3", 
            "birds": "https://cdn.pixabay.com/audio/forest-birds.mp3",
            "ocean": "https://cdn.pixabay.com/audio/ocean-waves.mp3"
        }
        
        if nature_sounds:
            for sound in nature_sounds:
                if sound in nature_library:
                    soundscape_config["layers"].append({
                        "type": "nature",
                        "sound": sound,
                        "url": nature_library[sound],
                        "volume": intensity * 0.3
                    })
        
        return soundscape_config

# Test the BGM system
if __name__ == "__main__":
    bgm = BGMSystem()
    
    # Test getting music for a theme
    music = bgm.get_music_for_theme("resilience")
    print("Selected music:", music["selected"]["name"])
    
    # Test audio config creation
    config = bgm.create_audio_config("resilience", 15)
    print("Audio config:", json.dumps(config, indent=2))