# video_generator/pixabay_service.py - Pixabay API integration for videos and audio
import requests
import random
import os
import tempfile
import urllib.parse
from typing import List, Dict, Optional
from .models import VideoFootage, AudioTrack, AudioSourceType

class PixabayService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('PIXABAY_API_KEY')
        if not self.api_key:
            raise ValueError("Pixabay API key is required. Set PIXABAY_API_KEY environment variable.")
        
        self.base_url = "https://pixabay.com/api/"
        self.session = requests.Session()
        
        print("✅ Pixabay service initialized")
    
    def search_motivation_videos(self) -> List[VideoFootage]:
        """Search for motivation video footage"""
        categories = ['alone', 'sea', 'mountain', 'forest', 'nature', 'landscape']
        
        all_videos = []
        for category in categories:
            try:
                videos = self._search_videos(category, video_type='motivation')
                all_videos.extend(videos)
            except Exception as e:
                print(f"Error searching videos for category {category}: {e}")
                continue
        
        # Remove duplicates and select best quality
        unique_videos = self._deduplicate_videos(all_videos)
        return self._filter_high_quality_videos(unique_videos)
    
    def search_lofi_videos(self) -> List[VideoFootage]:
        """Search for lofi/aesthetic video footage"""
        categories = ['interior', 'cafe', 'aesthetic', 'cozy', 'minimal', 'modern']
        
        all_videos = []
        for category in categories:
            try:
                videos = self._search_videos(category, video_type='lofi')
                all_videos.extend(videos)
            except Exception as e:
                print(f"Error searching videos for category {category}: {e}")
                continue
        
        unique_videos = self._deduplicate_videos(all_videos)
        return self._filter_high_quality_videos(unique_videos)
    
    def search_background_music(self) -> List[AudioTrack]:
        """Search for background music from Pixabay"""
        categories = [
            'nature', 'forest', 'ocean', 'peaceful', 'meditation', 
            'ambient', 'relaxing', 'calm', 'instrumental'
        ]
        
        all_audio = []
        for category in categories:
            try:
                audio_tracks = self._search_audio(category)
                all_audio.extend(audio_tracks)
            except Exception as e:
                print(f"Error searching audio for category {category}: {e}")
                continue
        
        # Filter for background music suitable for motivation videos
        filtered_audio = self._filter_background_music(all_audio)
        return filtered_audio
    
    def _search_videos(self, query: str, video_type: str = 'motivation') -> List[VideoFootage]:
        """Search videos on Pixabay"""
        params = {
            'key': self.api_key,
            'video_type': 'all',
            'category': 'nature' if video_type == 'motivation' else 'places',
            'min_width': 1920,
            'min_height': 1080,
            'min_duration': 20,
            'max_duration': 300,
            'per_page': 20,
            'safesearch': 'true',
            'q': query
        }
        
        try:
            response = self.session.get(f"{self.base_url}videos/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for hit in data.get('hits', []):
                video = VideoFootage(
                    id=str(hit['id']),
                    source='pixabay',
                    url=hit['videos']['large']['url'],
                    preview_url=hit['videos']['small']['url'],
                    tags=hit['tags'].split(', '),
                    duration=hit['duration'],
                    width=hit['videos']['large']['width'],
                    height=hit['videos']['large']['height'],
                    size=hit['videos']['large']['size'],
                    category=query
                )
                videos.append(video)
            
            return videos
            
        except Exception as e:
            print(f"Video search failed for query '{query}': {e}")
            return []
    
    def _search_audio(self, query: str) -> List[AudioTrack]:
        """Search background music on Pixabay"""
        params = {
            'key': self.api_key,
            'audio_type': 'music',
            'category': 'music',
            'min_duration': 30,
            'max_duration': 300,
            'per_page': 20,
            'safesearch': 'true',
            'q': query
        }
        
        try:
            # Note: Pixabay audio API endpoint
            response = self.session.get(f"{self.base_url}music/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            audio_tracks = []
            for hit in data.get('hits', []):
                track = AudioTrack(
                    id=str(hit['id']),
                    title=hit.get('title', hit['tags']),
                    source=AudioSourceType.PIXABAY_BGM,
                    url=hit['url'],
                    preview_url=hit['previewURL'],
                    duration=hit['duration'],
                    size=hit['size'],
                    category=query,
                    volume_level=0.20,  # 20% for background music
                    metadata={
                        'tags': hit['tags'],
                        'artist': hit.get('artist', 'Unknown'),
                        'pixabay_id': hit['id']
                    }
                )
                audio_tracks.append(track)
            
            return audio_tracks
            
        except Exception as e:
            print(f"Audio search failed for query '{query}': {e}")
            return []
    
    def _deduplicate_videos(self, videos: List[VideoFootage]) -> List[VideoFootage]:
        """Remove duplicate videos based on ID"""
        seen_ids = set()
        unique_videos = []
        
        for video in videos:
            if video.id not in seen_ids:
                seen_ids.add(video.id)
                unique_videos.append(video)
        
        return unique_videos
    
    def _filter_high_quality_videos(self, videos: List[VideoFootage]) -> List[VideoFootage]:
        """Filter videos for high quality and suitable content"""
        filtered = []
        
        for video in videos:
            # Quality filters
            if (video.width >= 1920 and 
                video.height >= 1080 and 
                video.duration >= 20 and 
                video.duration <= 300):
                
                # Content filters - avoid inappropriate tags
                inappropriate_tags = ['people', 'face', 'person', 'human', 'crowd']
                if not any(tag.lower() in ' '.join(video.tags).lower() for tag in inappropriate_tags):
                    filtered.append(video)
        
        return filtered
    
    def _filter_background_music(self, audio_tracks: List[AudioTrack]) -> List[AudioTrack]:
        """Filter audio tracks suitable for background music"""
        filtered = []
        
        for track in audio_tracks:
            # Duration filter for background music
            if 30 <= track.duration <= 300:
                # Prefer instrumental tracks
                tags_text = ' '.join(track.metadata.get('tags', '').split())
                
                if any(keyword in tags_text.lower() for keyword in 
                      ['instrumental', 'ambient', 'peaceful', 'nature', 'calm', 'meditation']):
                    filtered.append(track)
        
        return filtered
    
    def download_media(self, url: str, filename: str = None) -> str:
        """Download media file from URL"""
        if not filename:
            # Extract filename from URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = f"media_{random.randint(1000, 9999)}.mp4"
        
        # Create temp directory if it doesn't exist
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {filename}")
            return file_path
            
        except Exception as e:
            print(f"❌ Download failed for {url}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
    
    def get_random_video(self, video_type: str = 'motivation') -> Optional[VideoFootage]:
        """Get a random video of specified type"""
        if video_type == 'motivation':
            videos = self.search_motivation_videos()
        else:
            videos = self.search_lofi_videos()
        
        if videos:
            return random.choice(videos)
        return None
    
    def get_random_background_music(self) -> Optional[AudioTrack]:
        """Get random background music"""
        audio_tracks = self.search_background_music()
        if audio_tracks:
            return random.choice(audio_tracks)
        return None

# Lofi Music Library Service (separate from Pixabay)
class LofiMusicLibrary:
    """Dedicated service for high-quality Lofi music tracks"""
    
    def __init__(self):
        # Pre-curated lofi music library
        self.lofi_tracks = [
            {
                'id': 'lofi_001',
                'title': 'Peaceful Rain Study Session',
                'category': 'เงียบสงบ',
                'url': 'https://example.com/lofi/peaceful-rain.mp3',
                'duration': 180,
                'size': 7200000,  # ~7MB
                'genre': 'lofi-hip-hop',
                'mood': 'relaxing',
                'instruments': ['piano', 'rain-sounds', 'vinyl-crackle'],
                'bpm': 70
            },
            {
                'id': 'lofi_002',
                'title': 'Coffee Shop Morning Jazz',
                'category': 'แจ๊สสมูท',
                'url': 'https://example.com/lofi/coffee-jazz.mp3',
                'duration': 240,
                'size': 9600000,  # ~9.6MB
                'genre': 'jazz-lofi',
                'mood': 'cozy',
                'instruments': ['piano', 'soft-drums', 'double-bass', 'ambient'],
                'bpm': 75
            },
            {
                'id': 'lofi_003',
                'title': 'Acoustic Dreams',
                'category': 'อะคูสติก',
                'url': 'https://example.com/lofi/acoustic-dreams.mp3',
                'duration': 200,
                'size': 8000000,  # ~8MB
                'genre': 'acoustic-lofi',
                'mood': 'dreamy',
                'instruments': ['acoustic-guitar', 'strings', 'soft-percussion'],
                'bpm': 65
            },
            {
                'id': 'lofi_004',
                'title': 'Midnight Piano Sessions',
                'category': 'เปียโน',
                'url': 'https://example.com/lofi/midnight-piano.mp3',
                'duration': 220,
                'size': 8800000,  # ~8.8MB
                'genre': 'piano-lofi',
                'mood': 'contemplative',
                'instruments': ['piano', 'vinyl-noise', 'subtle-strings'],
                'bpm': 60
            },
            {
                'id': 'lofi_005',
                'title': 'Garden Meditation',
                'category': 'กีต้าร์โปร่ง',
                'url': 'https://example.com/lofi/garden-meditation.mp3',
                'duration': 190,
                'size': 7600000,  # ~7.6MB
                'genre': 'guitar-lofi',
                'mood': 'peaceful',
                'instruments': ['nylon-guitar', 'nature-sounds', 'soft-pads'],
                'bpm': 68
            }
        ]
    
    def search_tracks(self, categories: List[str]) -> List[AudioTrack]:
        """Search for lofi tracks by categories - DISABLED FOR PRODUCTION"""
        # Return empty list to disable all audio downloads
        return []
        
        # Original code disabled to prevent 404 errors from example.com URLs
        # This was causing: "Failed to download audio https://example.com/lofi/garden-meditation.mp3"
    
    def get_random_track(self) -> AudioTrack:
        """Get a random lofi track - DISABLED FOR PRODUCTION"""
        # Return None to disable random track selection
        return None
        
        # Original code disabled to prevent 404 errors from example.com URLs

# Test functions
def test_pixabay_service():
    """Test Pixabay service"""
    print("🔍 Testing Pixabay Service...")
    
    # Mock API key for testing
    service = PixabayService("demo-api-key")
    
    try:
        # Test video search
        videos = service.search_motivation_videos()
        print(f"📹 Found {len(videos)} motivation videos")
        
        if videos:
            video = videos[0]
            print(f"   Sample video: {video.id} - {video.tags[:3]}")
        
        # Test audio search
        audio = service.search_background_music()
        print(f"🎵 Found {len(audio)} background music tracks")
        
        if audio:
            track = audio[0]
            print(f"   Sample track: {track.title}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_lofi_library():
    """Test Lofi music library"""
    print("🎵 Testing Lofi Music Library...")
    
    library = LofiMusicLibrary()
    
    # Test search
    tracks = library.search_tracks(['เงียบสงบ', 'แจ๊สสมูท'])
    print(f"Found {len(tracks)} lofi tracks")
    
    for track in tracks:
        print(f"   {track.title} - {track.category} ({track.duration}s)")
    
    # Test random track
    random_track = library.get_random_track()
    print(f"Random track: {random_track.title}")

if __name__ == "__main__":
    test_pixabay_service()
    print()
    test_lofi_library()