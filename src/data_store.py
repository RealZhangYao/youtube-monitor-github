"""
Data storage using JSON files in the GitHub repository.
This replaces DynamoDB for GitHub Actions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataStore:
    """Manages data persistence using JSON files."""
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize data store."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.processed_videos_file = self.data_dir / 'processed_videos.json'
        self.transcripts_dir = self.data_dir / 'transcripts'
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Data store initialized at {self.data_dir}")
    
    def get_processed_videos(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get list of processed videos for a channel."""
        all_videos = self._load_processed_videos()
        channel_videos = all_videos.get(channel_id, [])
        
        # Sort by processed date, newest first
        channel_videos.sort(key=lambda x: x.get('processed_at', ''), reverse=True)
        
        return channel_videos
    
    def mark_video_processed(self, channel_id: str, video_id: str, 
                           video_info: Dict[str, Any], 
                           summary: str = "", 
                           email_sent: bool = False):
        """Mark a video as processed."""
        all_videos = self._load_processed_videos()
        
        if channel_id not in all_videos:
            all_videos[channel_id] = []
        
        # Create processed record
        processed_record = {
            'video_id': video_id,
            'title': video_info.get('title', 'Unknown'),
            'url': video_info.get('url', ''),
            'channel_title': video_info.get('channel_title', 'Unknown'),
            'published_at': str(video_info.get('published_at', '')),
            'processed_at': datetime.now().isoformat(),
            'summary': summary[:1000],  # Limit summary length
            'email_sent': email_sent,
            'duration': video_info.get('duration', 'Unknown'),
            'view_count': video_info.get('view_count', 0)
        }
        
        # Add to list
        all_videos[channel_id].append(processed_record)
        
        # Save
        self._save_processed_videos(all_videos)
        logger.info(f"Marked video as processed: {video_id}")
    
    def save_transcript(self, channel_id: str, video_id: str, 
                       transcript: str, language: Optional[str] = None):
        """Save video transcript to file."""
        # Create channel directory
        channel_dir = self.transcripts_dir / channel_id
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        # Save transcript
        transcript_file = channel_dir / f"{video_id}.json"
        
        transcript_data = {
            'video_id': video_id,
            'channel_id': channel_id,
            'language': language,
            'transcript': transcript,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved transcript for video: {video_id}")
    
    def get_transcript(self, channel_id: str, video_id: str) -> Optional[Dict[str, Any]]:
        """Get saved transcript for a video."""
        transcript_file = self.transcripts_dir / channel_id / f"{video_id}.json"
        
        if not transcript_file.exists():
            return None
        
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading transcript: {e}")
            return None
    
    def _load_processed_videos(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all processed videos from file."""
        if not self.processed_videos_file.exists():
            return {}
        
        try:
            with open(self.processed_videos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading processed videos: {e}")
            return {}
    
    def _save_processed_videos(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save processed videos to file."""
        try:
            with open(self.processed_videos_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving processed videos: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored data."""
        all_videos = self._load_processed_videos()
        
        total_videos = sum(len(videos) for videos in all_videos.values())
        total_channels = len(all_videos)
        
        # Count transcript files
        transcript_count = sum(1 for _ in self.transcripts_dir.rglob('*.json'))
        
        return {
            'total_channels': total_channels,
            'total_videos_processed': total_videos,
            'total_transcripts_saved': transcript_count,
            'data_directory': str(self.data_dir.absolute())
        }