"""
DownSub.com transcript fetcher module.

This module uses DownSub.com API to fetch video transcripts/subtitles.
It provides an alternative to youtube-transcript-api with better reliability.
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional, Tuple
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


class DownSubFetcher:
    """Fetches YouTube video transcripts using DownSub.com API."""

    def __init__(self):
        """Initialize DownSub fetcher."""
        self.base_url = "https://downsub.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("DownSub fetcher initialized")

    def fetch_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch transcript for a YouTube video using DownSub.com.

        Args:
            video_id: YouTube video ID

        Returns:
            Tuple of (transcript_text, language_code) or (None, None) if unavailable
        """
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Fetching transcript for video {video_id} using DownSub.com")

            # Step 1: Submit video URL to DownSub
            subtitles_info = self._get_subtitle_info(video_url)
            if not subtitles_info:
                logger.warning(f"No subtitle info found for video {video_id}")
                return None, None

            # Step 2: Find best subtitle track
            best_subtitle = self._select_best_subtitle(subtitles_info)
            if not best_subtitle:
                logger.warning(f"No suitable subtitle found for video {video_id}")
                return None, None

            # Step 3: Download subtitle content
            transcript_text = self._download_subtitle(best_subtitle)
            if not transcript_text:
                logger.warning(f"Failed to download subtitle for video {video_id}")
                return None, None

            language_code = best_subtitle.get('language', 'unknown')
            logger.info(f"Successfully fetched transcript for video {video_id} in {language_code}")

            return transcript_text, language_code

        except Exception as e:
            logger.error(f"Error fetching transcript for video {video_id}: {e}")
            return None, None

    def _get_subtitle_info(self, video_url: str) -> Optional[List[Dict]]:
        """
        Get available subtitle information from DownSub.com.

        Args:
            video_url: YouTube video URL

        Returns:
            List of available subtitle tracks or None
        """
        try:
            # Method 1: Try direct API approach
            api_url = f"{self.base_url}/api/subtitles"
            data = {
                'url': video_url,
                'format': 'json'
            }

            response = self.session.post(api_url, data=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('subtitles'):
                    return result['subtitles']

            # Method 2: Try web scraping approach
            return self._scrape_subtitle_info(video_url)

        except Exception as e:
            logger.error(f"Error getting subtitle info: {e}")
            return None

    def _scrape_subtitle_info(self, video_url: str) -> Optional[List[Dict]]:
        """
        Scrape subtitle information from DownSub.com web interface.

        Args:
            video_url: YouTube video URL

        Returns:
            List of available subtitle tracks or None
        """
        try:
            # Visit the main page
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                return None

            # Submit the video URL
            data = {
                'supported_sites': video_url,
                'submit': 'Download'
            }

            response = self.session.post(self.base_url, data=data, timeout=30)
            if response.status_code != 200:
                return None

            # Parse the response to extract subtitle links
            return self._parse_subtitle_links(response.text)

        except Exception as e:
            logger.error(f"Error scraping subtitle info: {e}")
            return None

    def _parse_subtitle_links(self, html_content: str) -> Optional[List[Dict]]:
        """
        Parse HTML content to extract subtitle download links.

        Args:
            html_content: HTML content from DownSub.com

        Returns:
            List of subtitle tracks or None
        """
        try:
            import re

            # Look for subtitle download links
            # Pattern to match subtitle links
            pattern = r'href="([^"]*\.(?:srt|vtt|txt)[^"]*)"[^>]*>([^<]*(?:English|Chinese|Auto|Manual)[^<]*)'
            matches = re.findall(pattern, html_content, re.IGNORECASE)

            subtitles = []
            for url, description in matches:
                # Make URL absolute if relative
                if url.startswith('/'):
                    url = self.base_url + url

                # Determine language from description
                language = 'en'  # default
                if 'chinese' in description.lower() or '中文' in description:
                    language = 'zh'
                elif 'english' in description.lower():
                    language = 'en'

                subtitles.append({
                    'url': url,
                    'language': language,
                    'description': description.strip(),
                    'auto_generated': 'auto' in description.lower()
                })

            return subtitles if subtitles else None

        except Exception as e:
            logger.error(f"Error parsing subtitle links: {e}")
            return None

    def _select_best_subtitle(self, subtitles: List[Dict]) -> Optional[Dict]:
        """
        Select the best subtitle track from available options.

        Args:
            subtitles: List of available subtitle tracks

        Returns:
            Best subtitle track or None
        """
        if not subtitles:
            return None

        # Preference order: English manual > English auto > Chinese manual > Chinese auto > any other
        preferences = [
            {'language': 'en', 'auto_generated': False},
            {'language': 'en', 'auto_generated': True},
            {'language': 'zh', 'auto_generated': False},
            {'language': 'zh', 'auto_generated': True},
        ]

        for pref in preferences:
            for subtitle in subtitles:
                if (subtitle.get('language') == pref['language'] and
                    subtitle.get('auto_generated') == pref['auto_generated']):
                    return subtitle

        # If no preferred subtitle found, return the first one
        return subtitles[0]

    def _download_subtitle(self, subtitle_info: Dict) -> Optional[str]:
        """
        Download subtitle content from the given URL.

        Args:
            subtitle_info: Subtitle track information

        Returns:
            Subtitle content as text or None
        """
        try:
            url = subtitle_info['url']
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to download subtitle: HTTP {response.status_code}")
                return None

            # Convert subtitle content to plain text
            content = response.text

            # If it's SRT format, extract just the text
            if url.endswith('.srt'):
                content = self._srt_to_text(content)
            elif url.endswith('.vtt'):
                content = self._vtt_to_text(content)

            return content

        except Exception as e:
            logger.error(f"Error downloading subtitle: {e}")
            return None

    def _srt_to_text(self, srt_content: str) -> str:
        """
        Convert SRT subtitle format to plain text.

        Args:
            srt_content: SRT format subtitle content

        Returns:
            Plain text content
        """
        try:
            import re

            # Remove SRT formatting (numbers, timestamps, etc.)
            # Pattern to match SRT entries: number, timestamp, text
            pattern = r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.*?)(?=\n\d+\n|\n*$)'

            matches = re.findall(pattern, srt_content, re.DOTALL)

            # Join all text parts
            text_parts = []
            for match in matches:
                # Clean up the text (remove HTML tags, extra whitespace)
                clean_text = re.sub(r'<[^>]+>', '', match)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                if clean_text:
                    text_parts.append(clean_text)

            return ' '.join(text_parts)

        except Exception as e:
            logger.error(f"Error converting SRT to text: {e}")
            return srt_content

    def _vtt_to_text(self, vtt_content: str) -> str:
        """
        Convert VTT subtitle format to plain text.

        Args:
            vtt_content: VTT format subtitle content

        Returns:
            Plain text content
        """
        try:
            import re

            # Remove VTT formatting
            lines = vtt_content.split('\n')
            text_parts = []

            for line in lines:
                line = line.strip()
                # Skip header, timestamps, and empty lines
                if (line.startswith('WEBVTT') or
                    '-->' in line or
                    not line or
                    line.isdigit()):
                    continue

                # Clean up the text
                clean_text = re.sub(r'<[^>]+>', '', line)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                if clean_text:
                    text_parts.append(clean_text)

            return ' '.join(text_parts)

        except Exception as e:
            logger.error(f"Error converting VTT to text: {e}")
            return vtt_content