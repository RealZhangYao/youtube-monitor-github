"""
YouTube API client for fetching channel and video information.

This module provides a wrapper around the YouTube Data API v3
to fetch channel updates and video metadata.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeClient:
    """Client for interacting with YouTube Data API v3."""
    
    def __init__(self, api_key: str):
        """
        Initialize YouTube client.
        
        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        logger.info("YouTube client initialized")
    
    def get_channel_id_by_username(self, username: str) -> Optional[str]:
        """
        Get channel ID from username (handle like @lidangzzz).

        Args:
            username: YouTube username/handle (with or without @)

        Returns:
            Channel ID or None if not found
        """
        try:
            # Remove @ if present
            clean_username = username.lstrip('@')

            # Try forUsername parameter first
            request = self.youtube.channels().list(
                part='id',
                forUsername=clean_username
            )
            response = request.execute()

            if response.get('items'):
                return response['items'][0]['id']

            # If forUsername doesn't work, try handle parameter (newer format)
            request = self.youtube.channels().list(
                part='id',
                forHandle=clean_username
            )
            response = request.execute()

            if response.get('items'):
                return response['items'][0]['id']

            logger.warning(f"Channel not found for username: {username}")
            return None

        except HttpError as e:
            logger.error(f"YouTube API error for username {username}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting channel ID: {e}")
            return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel information including title and uploads playlist ID.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Channel info dict or None if not found
        """
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails',
                id=channel_id
            )
            response = request.execute()

            if not response.get('items'):
                logger.warning(f"Channel not found: {channel_id}")
                return None

            channel = response['items'][0]
            return {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', ''),
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
                'thumbnail_url': channel['snippet']['thumbnails']['high']['url']
            }

        except HttpError as e:
            logger.error(f"YouTube API error for channel {channel_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting channel info: {e}")
            return None
    
    def get_latest_videos(self, 
                         channel_id: str, 
                         max_results: int = 5,
                         published_after: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get latest videos from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return
            published_after: Only return videos published after this datetime
            
        Returns:
            List of video information dictionaries
        """
        try:
            # Get channel info first to get uploads playlist
            channel_info = self.get_channel_info(channel_id)
            if not channel_info:
                return []
            
            uploads_playlist_id = channel_info['uploads_playlist_id']
            
            # Get videos from uploads playlist
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_snippet = item['snippet']
                video_id = video_snippet['resourceId']['videoId']
                
                # Get detailed video info
                video_details = self.get_video_details(video_id)
                if not video_details:
                    continue
                
                # Parse published date
                published_at = datetime.fromisoformat(
                    video_snippet['publishedAt'].replace('Z', '+00:00')
                )
                
                # Filter by published_after if provided
                if published_after and published_at <= published_after:
                    logger.debug(f"Skipping old video: {video_snippet['title']}")
                    continue
                
                videos.append({
                    'id': video_id,
                    'title': video_snippet['title'],
                    'description': video_snippet.get('description', ''),
                    'published_at': published_at,
                    'channel_id': channel_id,
                    'channel_title': channel_info['title'],
                    'thumbnail_url': video_snippet['thumbnails']['high']['url'],
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'duration': video_details.get('duration', 'Unknown'),
                    'view_count': video_details.get('view_count', 0),
                    'like_count': video_details.get('like_count', 0)
                })
            
            # Sort by published date (newest first)
            videos.sort(key=lambda x: x['published_at'], reverse=True)
            
            logger.info(f"Found {len(videos)} new videos for channel {channel_id}")
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error for channel {channel_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting videos: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video details dict or None if not found
        """
        try:
            request = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                logger.warning(f"Video not found: {video_id}")
                return None
            
            video = response['items'][0]
            
            # Parse duration from ISO 8601 format
            duration_str = video['contentDetails']['duration']
            duration = self._parse_duration(duration_str)
            
            return {
                'duration': duration,
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0))
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error for video {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting video details: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> str:
        """
        Parse ISO 8601 duration to human-readable format.
        
        Args:
            duration_str: Duration in ISO 8601 format (e.g., PT4M13S)
            
        Returns:
            Human-readable duration (e.g., "4:13")
        """
        try:
            # Remove PT prefix
            duration_str = duration_str.replace('PT', '')
            
            hours = 0
            minutes = 0
            seconds = 0
            
            # Parse hours
            if 'H' in duration_str:
                hours, duration_str = duration_str.split('H')
                hours = int(hours)
            
            # Parse minutes
            if 'M' in duration_str:
                minutes, duration_str = duration_str.split('M')
                minutes = int(minutes)
            
            # Parse seconds
            if 'S' in duration_str:
                seconds = duration_str.replace('S', '')
                seconds = int(seconds)
            
            # Format duration
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
                
        except Exception as e:
            logger.error(f"Error parsing duration {duration_str}: {e}")
            return "Unknown"
    
    def check_api_quota(self) -> bool:
        """
        Check if API quota is available by making a simple request.
        
        Returns:
            True if API is accessible, False if quota exceeded
        """
        try:
            # Make a simple request to check quota
            request = self.youtube.videos().list(
                part='id',
                id='dQw4w9WgXcQ'  # Use a known video ID
            )
            request.execute()
            return True
            
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                logger.error("YouTube API quota exceeded")
                return False
            logger.error(f"YouTube API error checking quota: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking API quota: {e}")
            return False


