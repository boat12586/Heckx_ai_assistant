#!/usr/bin/env python3
"""
Google Drive Integration Service
Handles file uploads and management for music library
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google API libraries not installed. Run: pip install google-api-python-client google-auth google-auth-oauthlib")

class GoogleDriveService:
    def __init__(self):
        self.credentials_file = 'google_credentials.json'
        self.token_file = 'google_token.json'
        self.scopes = ['https://www.googleapis.com/auth/drive.file']
        self.service = None
        self.folder_id = None
        self.init_drive_connection()
    
    def init_drive_connection(self):
        """Initialize Google Drive connection"""
        if not GOOGLE_AVAILABLE:
            print("Google Drive integration disabled - missing dependencies")
            return False
        
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(self.credentials_file):
                        flow = Flow.from_client_secrets_file(self.credentials_file, self.scopes)
                        flow.redirect_uri = 'http://localhost:8080'
                        
                        # Generate authorization URL
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        print(f"Please visit this URL to authorize: {auth_url}")
                        
                        # Wait for authorization code
                        auth_code = input('Enter the authorization code: ')
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                    else:
                        print("Google credentials file not found. Please add google_credentials.json")
                        return False
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            self.ensure_music_folder()
            return True
            
        except Exception as e:
            print(f"Google Drive connection error: {str(e)}")
            return False
    
    def ensure_music_folder(self):
        """Create or find Heckx Music folder in Google Drive"""
        if not self.service:
            return
        
        try:
            # Search for existing folder
            results = self.service.files().list(
                q="name='Heckx Music Library' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
                print(f"Using existing folder: {folders[0]['name']}")
            else:
                # Create new folder
                folder_metadata = {
                    'name': 'Heckx Music Library',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(body=folder_metadata, fields='id').execute()
                self.folder_id = folder.get('id')
                print(f"Created new folder: Heckx Music Library")
                
        except Exception as e:
            print(f"Error creating/finding folder: {str(e)}")
    
    def upload_music_file(self, file_path: str, track_info: Dict) -> Optional[str]:
        """Upload music file to Google Drive"""
        if not self.service or not self.folder_id:
            print("Google Drive not initialized")
            return None
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return None
            
            # Prepare file metadata
            file_metadata = {
                'name': file_path.name,
                'parents': [self.folder_id],
                'description': f"Artist: {track_info.get('artist', 'Unknown')}\n"
                             f"Genre: {track_info.get('genre', 'Unknown')}\n"
                             f"Mood: {track_info.get('mood', 'Unknown')}\n"
                             f"Downloads: {track_info.get('downloads', 0)}\n"
                             f"Source: {track_info.get('source', 'Unknown')}"
            }
            
            # Upload file
            media = MediaFileUpload(
                str(file_path),
                mimetype='audio/mpeg',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            print(f"✅ Uploaded to Google Drive: {file_path.name}")
            
            # Update database with Google Drive ID
            self._update_track_drive_id(track_info.get('external_id'), file_id)
            
            return file_id
            
        except Exception as e:
            print(f"Upload error for {file_path}: {str(e)}")
            return None
    
    def _update_track_drive_id(self, external_id: str, drive_id: str):
        """Update track with Google Drive ID"""
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE music_tracks 
            SET google_drive_id = ? 
            WHERE external_id = ?
        ''', (drive_id, external_id))
        
        conn.commit()
        conn.close()
    
    def bulk_upload_library(self):
        """Upload all downloaded music to Google Drive"""
        if not self.service:
            print("Google Drive not available")
            return
        
        # Get all tracks with local files but no Drive ID
        conn = sqlite3.connect('music_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT external_id, title, artist, file_path, genre, mood, downloads, source
            FROM music_tracks 
            WHERE file_path IS NOT NULL 
            AND (google_drive_id IS NULL OR google_drive_id = '')
        ''')
        
        tracks = cursor.fetchall()
        conn.close()
        
        print(f"Uploading {len(tracks)} tracks to Google Drive...")
        
        for track in tracks:
            track_info = {
                'external_id': track[0],
                'title': track[1],
                'artist': track[2],
                'genre': track[4],
                'mood': track[5],
                'downloads': track[6],
                'source': track[7]
            }
            
            self.upload_music_file(track[3], track_info)
    
    def get_drive_library_info(self) -> Dict:
        """Get information about music library in Google Drive"""
        if not self.service or not self.folder_id:
            return {'error': 'Google Drive not available'}
        
        try:
            # Get all files in music folder
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents",
                fields="files(id, name, size, createdTime, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            
            total_size = 0
            audio_files = []
            
            for file in files:
                if file.get('mimeType', '').startswith('audio/'):
                    size = int(file.get('size', 0))
                    total_size += size
                    audio_files.append({
                        'name': file['name'],
                        'size_mb': round(size / (1024 * 1024), 2),
                        'created': file.get('createdTime', ''),
                        'id': file['id']
                    })
            
            return {
                'total_files': len(audio_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files': audio_files[:10],  # Show first 10 files
                'folder_id': self.folder_id
            }
            
        except Exception as e:
            return {'error': f'Failed to get Drive info: {str(e)}'}
    
    def download_from_drive(self, file_id: str, local_path: str) -> bool:
        """Download file from Google Drive"""
        if not self.service:
            return False
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            print(f"Downloaded from Drive: {local_path}")
            return True
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            return False
    
    def create_shared_playlist_link(self, playlist_name: str, track_ids: List[str]) -> Optional[str]:
        """Create a shareable link for a playlist"""
        if not self.service or not self.folder_id:
            return None
        
        try:
            # Create playlist folder
            playlist_metadata = {
                'name': f"Playlist - {playlist_name}",
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.folder_id]
            }
            
            playlist_folder = self.service.files().create(
                body=playlist_metadata,
                fields='id'
            ).execute()
            
            playlist_folder_id = playlist_folder.get('id')
            
            # Make folder shareable
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            self.service.permissions().create(
                fileId=playlist_folder_id,
                body=permission
            ).execute()
            
            # Get shareable link
            folder_info = self.service.files().get(
                fileId=playlist_folder_id,
                fields='webViewLink'
            ).execute()
            
            return folder_info.get('webViewLink')
            
        except Exception as e:
            print(f"Error creating shared playlist: {str(e)}")
            return None

class MockGoogleDriveService:
    """Mock service when Google APIs are not available"""
    
    def __init__(self):
        self.mock_mode = True
        print("🔧 Running in mock mode - Google Drive features simulated")
    
    def upload_music_file(self, file_path: str, track_info: Dict) -> Optional[str]:
        print(f"📤 [MOCK] Would upload: {Path(file_path).name}")
        return f"mock_drive_id_{hash(file_path) % 10000}"
    
    def bulk_upload_library(self):
        print("📤 [MOCK] Would bulk upload library to Google Drive")
    
    def get_drive_library_info(self) -> Dict:
        return {
            'mock_mode': True,
            'total_files': 0,
            'total_size_mb': 0,
            'message': 'Google Drive mock mode - install google-api-python-client to enable'
        }

def get_drive_service():
    """Get Google Drive service (real or mock)"""
    if GOOGLE_AVAILABLE:
        return GoogleDriveService()
    else:
        return MockGoogleDriveService()

if __name__ == "__main__":
    # Test the service
    drive = get_drive_service()
    info = drive.get_drive_library_info()
    print(json.dumps(info, indent=2))