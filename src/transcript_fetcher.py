"""
YouTube transcript fetcher module.

This module uses youtube-transcript-api to fetch video transcripts/subtitles.
It handles multiple languages and provides fallback options.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    TooManyRequests
)

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
            return None, None
        except VideoUnavailable:
            logger.warning(f"Video {video_id} is unavailable")
            return None, None
        except TooManyRequests:
            logger.error(f"Too many requests to YouTube for video {video_id}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript for video {video_id}: {e}")
            return None, None
    
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


