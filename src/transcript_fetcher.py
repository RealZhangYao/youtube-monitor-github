"""
YouTube transcript fetcher module.

This module uses youtube-transcript-api to fetch video transcripts/subtitles.
It handles multiple languages and provides fallback options.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import tempfile
import os

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

# TooManyRequests might not be available in newer versions
try:
    from youtube_transcript_api._errors import TooManyRequests
except ImportError:
    TooManyRequests = Exception
import yt_dlp

logger = logging.getLogger(__name__)


class TranscriptFetcher:
    """Fetches and processes YouTube video transcripts."""
    
    # Preferred languages in order of preference
    PREFERRED_LANGUAGES = ['en', 'en-US', 'en-GB']
    
    # Fallback to auto-generated captions if manual ones aren't available
    ALLOW_AUTO_GENERATED = True
    
    def __init__(self):
        """Initialize transcript fetcher."""
        logger.info("Transcript fetcher initialized")
    
    def fetch_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple of (transcript_text, language_code) or (None, None) if unavailable
        """
        try:
            # Get list of available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get transcript in preferred languages
            transcript = None
            language_code = None
            
            # First try manual transcripts in preferred languages
            for lang in self.PREFERRED_LANGUAGES:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    language_code = lang
                    logger.info(f"Found manual transcript for video {video_id} in {lang}")
                    break
                except NoTranscriptFound:
                    continue
            
            # If no manual transcript found and auto-generated allowed
            if not transcript and self.ALLOW_AUTO_GENERATED:
                try:
                    # Try to get auto-generated transcript
                    for lang in self.PREFERRED_LANGUAGES:
                        try:
                            transcript = transcript_list.find_generated_transcript([lang])
                            language_code = f"{lang}-auto"
                            logger.info(f"Found auto-generated transcript for video {video_id} in {lang}")
                            break
                        except NoTranscriptFound:
                            continue
                except Exception as e:
                    logger.debug(f"No auto-generated transcript found: {e}")
            
            # If still no transcript, try any available language
            if not transcript:
                try:
                    # Get first available transcript
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                        language_code = transcript.language_code
                        logger.info(f"Using transcript in {language_code} for video {video_id}")
                except Exception as e:
                    logger.error(f"Error getting any transcript: {e}")
            
            if not transcript:
                logger.warning(f"No transcript available for video {video_id}")
                return None, None
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            # Process and combine transcript segments
            full_text = self._process_transcript_data(transcript_data)
            
            return full_text, language_code
            
        except TranscriptsDisabled:
            logger.warning(f"Transcripts are disabled for video {video_id}")
            # Try yt-dlp as fallback
            return self._fetch_with_ytdlp(video_id)
        except VideoUnavailable:
            logger.warning(f"Video {video_id} is unavailable")
            return None, None
        except TooManyRequests:
            logger.error(f"Too many requests to YouTube for video {video_id}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript for video {video_id}: {e}")
            # Try yt-dlp as fallback
            return self._fetch_with_ytdlp(video_id)
    
    def _process_transcript_data(self, transcript_data: List[Dict[str, Any]]) -> str:
        """
        Process raw transcript data into clean text.
        
        Args:
            transcript_data: List of transcript segments with text, start, and duration
            
        Returns:
            Processed transcript text
        """
        try:
            # Combine all text segments
            text_segments = []
            
            for segment in transcript_data:
                text = segment.get('text', '').strip()
                if text:
                    # Clean up common transcript artifacts
                    text = text.replace('\n', ' ')
                    text = text.replace('  ', ' ')
                    text_segments.append(text)
            
            # Join segments with spaces
            full_text = ' '.join(text_segments)
            
            # Additional cleanup
            full_text = self._clean_transcript_text(full_text)
            
            logger.info(f"Processed transcript with {len(text_segments)} segments, "
                       f"total length: {len(full_text)} characters")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing transcript data: {e}")
            return ""
    
    def _clean_transcript_text(self, text: str) -> str:
        """
        Clean transcript text by removing artifacts and formatting issues.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned transcript text
        """
        # Remove multiple spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        # Remove music/sound annotations if present
        import re
        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
        text = re.sub(r'\(.*?\)', '', text)  # Remove (Music), (Applause), etc.
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def get_transcript_with_timestamps(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get transcript with timestamp information preserved.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of transcript segments with timestamps or None
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get transcript (similar logic as fetch_transcript)
            transcript = None
            for lang in self.PREFERRED_LANGUAGES:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except NoTranscriptFound:
                    continue
            
            if not transcript:
                # Try auto-generated
                for lang in self.PREFERRED_LANGUAGES:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        break
                    except NoTranscriptFound:
                        continue
            
            if not transcript:
                return None
            
            # Fetch transcript data with timestamps
            transcript_data = transcript.fetch()
            
            # Clean text while preserving timestamps
            cleaned_data = []
            for segment in transcript_data:
                cleaned_segment = {
                    'text': segment['text'].strip(),
                    'start': segment['start'],
                    'duration': segment['duration'],
                    'end': segment['start'] + segment['duration']
                }
                if cleaned_segment['text']:
                    cleaned_data.append(cleaned_segment)
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error getting transcript with timestamps for video {video_id}: {e}")
            return None
    
    def _fetch_with_ytdlp(self, video_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch transcript using yt-dlp as a fallback option.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple of (transcript_text, language_code) or (None, None) if unavailable
        """
        logger.info(f"Attempting to fetch transcript with yt-dlp for video {video_id}")
        
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Configure yt-dlp options
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,  # Get auto-generated subtitles
                'subtitlesformat': 'json3/srv3/srv2/srv1/vtt/best',
                'skip_download': True,  # Don't download the video
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                # Add headers to avoid bot detection
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                # Add cookies file support (optional)
                # 'cookiesfrombrowser': 'chrome',  # or 'firefox', 'edge', etc.
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(video_url, download=False)
                
                # Check for subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # Try to get subtitles in preferred languages
                transcript_text = None
                language_code = None
                
                # First try manual subtitles
                for lang in self.PREFERRED_LANGUAGES + ['zh-CN', 'zh-TW', 'zh', 'zh-Hans', 'zh-Hant']:
                    if lang in subtitles:
                        sub_info = subtitles[lang]
                        transcript_text = self._download_and_parse_subtitle(sub_info)
                        if transcript_text:
                            language_code = lang
                            logger.info(f"Found manual subtitles in {lang} using yt-dlp")
                            break
                
                # If no manual subtitles, try auto-generated
                if not transcript_text:
                    for lang in self.PREFERRED_LANGUAGES + ['zh-CN', 'zh-TW', 'zh', 'zh-Hans', 'zh-Hant']:
                        if lang in automatic_captions:
                            sub_info = automatic_captions[lang]
                            transcript_text = self._download_and_parse_subtitle(sub_info)
                            if transcript_text:
                                language_code = f"{lang}-auto"
                                logger.info(f"Found auto-generated subtitles in {lang} using yt-dlp")
                                break
                
                # If still no transcript in preferred languages, try any available
                if not transcript_text:
                    all_langs = list(subtitles.keys()) + list(automatic_captions.keys())
                    if all_langs:
                        lang = all_langs[0]
                        sub_info = subtitles.get(lang, automatic_captions.get(lang))
                        transcript_text = self._download_and_parse_subtitle(sub_info)
                        if transcript_text:
                            language_code = lang
                            logger.info(f"Found subtitles in {lang} using yt-dlp (fallback language)")
                
                if transcript_text:
                    return transcript_text, language_code
                else:
                    logger.warning(f"No subtitles found using yt-dlp for video {video_id}")
                    return None, None
                    
        except Exception as e:
            logger.error(f"Error using yt-dlp for video {video_id}: {e}")
            return None, None
    
    def _download_and_parse_subtitle(self, subtitle_info: List[Dict]) -> Optional[str]:
        """
        Download and parse subtitle data from yt-dlp subtitle info.
        
        Args:
            subtitle_info: List of subtitle format options from yt-dlp
            
        Returns:
            Parsed subtitle text or None
        """
        try:
            import requests
            
            # Find a suitable subtitle format
            for sub_format in subtitle_info:
                if sub_format.get('ext') in ['json3', 'srv1', 'srv2', 'srv3', 'vtt']:
                    url = sub_format.get('url')
                    if url:
                        response = requests.get(url, timeout=30)
                        response.raise_for_status()
                        
                        # Parse based on format
                        if sub_format['ext'] == 'json3':
                            return self._parse_json3_subtitle(response.text)
                        elif sub_format['ext'] in ['srv1', 'srv2', 'srv3']:
                            return self._parse_srv_subtitle(response.text)
                        elif sub_format['ext'] == 'vtt':
                            return self._parse_vtt_subtitle(response.text)
                        
            return None
            
        except Exception as e:
            logger.error(f"Error downloading/parsing subtitle: {e}")
            return None
    
    def _parse_json3_subtitle(self, content: str) -> Optional[str]:
        """Parse JSON3 format subtitle."""
        try:
            data = json.loads(content)
            events = data.get('events', [])
            
            text_segments = []
            for event in events:
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            text_segments.append(seg['utf8'])
            
            return ' '.join(text_segments)
            
        except Exception as e:
            logger.error(f"Error parsing JSON3 subtitle: {e}")
            return None
    
    def _parse_srv_subtitle(self, content: str) -> Optional[str]:
        """Parse SRV format subtitle (XML)."""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            
            text_segments = []
            for text_elem in root.findall('.//text'):
                if text_elem.text:
                    text_segments.append(text_elem.text.strip())
            
            return ' '.join(text_segments)
            
        except Exception as e:
            logger.error(f"Error parsing SRV subtitle: {e}")
            return None
    
    def _parse_vtt_subtitle(self, content: str) -> Optional[str]:
        """Parse WebVTT format subtitle."""
        try:
            lines = content.split('\n')
            text_segments = []
            
            for line in lines:
                line = line.strip()
                # Skip headers, timestamps, and empty lines
                if line and not line.startswith('WEBVTT') and '-->' not in line and not line.isdigit():
                    text_segments.append(line)
            
            return ' '.join(text_segments)
            
        except Exception as e:
            logger.error(f"Error parsing VTT subtitle: {e}")
            return None
    
    def format_transcript_for_display(self, 
                                    transcript_data: List[Dict[str, Any]], 
                                    include_timestamps: bool = False) -> str:
        """
        Format transcript data for display or storage.
        
        Args:
            transcript_data: List of transcript segments
            include_timestamps: Whether to include timestamps in output
            
        Returns:
            Formatted transcript text
        """
        if not transcript_data:
            return ""
        
        formatted_lines = []
        
        for segment in transcript_data:
            if include_timestamps:
                # Format timestamp as [MM:SS]
                start_time = segment['start']
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                formatted_lines.append(f"{timestamp} {segment['text']}")
            else:
                formatted_lines.append(segment['text'])
        
        return '\n'.join(formatted_lines) if include_timestamps else ' '.join(formatted_lines)


