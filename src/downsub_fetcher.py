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

        Note: DownSub.com is a JavaScript-based application, so this implementation
        will attempt to access it but may fail due to dynamic content loading.
        This serves as a placeholder for potential future improvements.

        Args:
            video_id: YouTube video ID

        Returns:
            Tuple of (transcript_text, language_code) or (None, None) if unavailable
        """
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.debug(f"Attempting to fetch transcript for video {video_id} using DownSub.com")

            # Note: DownSub.com requires JavaScript for full functionality
            # This is a simplified attempt that will likely fail but provides
            # framework for future enhancement

            subtitles_info = self._get_subtitle_info(video_url)
            if not subtitles_info:
                logger.debug(f"DownSub.com: No subtitle info found for video {video_id}")
                return None, None

            # Find best subtitle track
            best_subtitle = self._select_best_subtitle(subtitles_info)
            if not best_subtitle:
                logger.debug(f"DownSub.com: No suitable subtitle found for video {video_id}")
                return None, None

            # Download subtitle content
            transcript_text = self._download_subtitle(best_subtitle)
            if not transcript_text:
                logger.debug(f"DownSub.com: Failed to download subtitle for video {video_id}")
                return None, None

            language_code = best_subtitle.get('language', 'unknown')
            logger.info(f"✅ DownSub.com: Successfully fetched transcript for video {video_id} in {language_code}")

            return transcript_text, language_code

        except Exception as e:
            logger.debug(f"DownSub.com failed for video {video_id}: {e}")
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
            # Method 1: Try web scraping approach (more reliable)
            logger.debug(f"Trying web scraping approach for {video_url}")
            result = self._scrape_subtitle_info(video_url)
            if result:
                return result

            # Method 2: Try different API approaches
            api_endpoints = [
                f"{self.base_url}/api/subtitles",
                f"{self.base_url}/api/download"
            ]

            for api_url in api_endpoints:
                try:
                    logger.debug(f"Trying API endpoint: {api_url}")
                    data = {
                        'url': video_url,
                        'format': 'json'
                    }

                    response = self.session.post(api_url, data=data, timeout=30)
                    logger.debug(f"API response status: {response.status_code}")

                    if response.status_code == 200:
                        # Try to parse as JSON first
                        try:
                            result = response.json()
                            if result.get('subtitles'):
                                return result['subtitles']
                        except:
                            # If not JSON, try to parse as HTML
                            return self._parse_subtitle_links(response.text)

                except Exception as e:
                    logger.debug(f"API endpoint {api_url} failed: {e}")
                    continue

            return None

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
            # Method 1: Try direct URL construction (like the link you showed)
            import urllib.parse
            encoded_url = urllib.parse.quote(video_url, safe='')
            direct_url = f"{self.base_url}/?url={encoded_url}"

            logger.debug(f"Trying direct URL: {direct_url}")
            response = self.session.get(direct_url, timeout=30)

            if response.status_code == 200:
                result = self._parse_subtitle_links(response.text)
                if result:
                    logger.debug(f"Found {len(result)} subtitle tracks via direct URL")
                    return result

            # Method 2: Traditional form submission
            logger.debug("Trying form submission method...")
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Failed to access DownSub.com: {response.status_code}")
                return None

            # Try different form field names that DownSub might use
            form_fields = [
                {'url': video_url},
                {'supported_sites': video_url, 'submit': 'Download'},
                {'video_url': video_url, 'download': '1'},
                {'link': video_url, 'action': 'download'}
            ]

            for data in form_fields:
                try:
                    logger.debug(f"Trying form data: {data}")
                    response = self.session.post(self.base_url, data=data, timeout=30)

                    if response.status_code == 200:
                        # Parse the response to extract subtitle links
                        result = self._parse_subtitle_links(response.text)
                        if result:
                            logger.debug(f"Found {len(result)} subtitle tracks via form")
                            return result

                except Exception as e:
                    logger.debug(f"Form submission failed: {e}")
                    continue

            return None

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
            from bs4 import BeautifulSoup

            subtitles = []

            # Method 1: Use BeautifulSoup for more reliable parsing
            try:
                soup = BeautifulSoup(html_content, 'html.parser')  # Use built-in parser

                # Look for download links with subtitle file extensions
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text(strip=True)

                    # Check if this is a subtitle file
                    if any(ext in href.lower() for ext in ['.srt', '.vtt', '.txt', '.sbv']):
                        # Make URL absolute if relative
                        if href.startswith('/'):
                            url = self.base_url + href
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = f"{self.base_url}/{href}"

                        # Determine language and type from link text or href
                        language = 'en'  # default
                        auto_generated = False

                        if any(term in text.lower() for term in ['chinese', '中文', 'zh']):
                            language = 'zh'
                        elif any(term in text.lower() for term in ['english', 'en']):
                            language = 'en'

                        if any(term in text.lower() for term in ['auto', 'automatic', 'generated']):
                            auto_generated = True

                        subtitles.append({
                            'url': url,
                            'language': language,
                            'description': text or 'Subtitle',
                            'auto_generated': auto_generated
                        })

            except ImportError:
                logger.debug("BeautifulSoup not available, using regex")

            # Method 2: Regex patterns for different subtitle formats
            patterns = [
                # Pattern for direct subtitle file links
                r'href="([^"]*\.(?:srt|vtt|txt|sbv)[^"]*)"[^>]*>([^<]*)',
                # Pattern for download buttons/links
                r'href="([^"]*download[^"]*(?:srt|vtt|txt)[^"]*)"[^>]*>([^<]*)',
                # General download links
                r'<a[^>]*href="([^"]*)"[^>]*>[^<]*(?:download|下载)[^<]*</a>',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if len(match) >= 2:
                        url, description = match[0], match[1]
                    else:
                        url, description = match[0], 'Subtitle'

                    # Skip if already found
                    if any(sub['url'] == url for sub in subtitles):
                        continue

                    # Make URL absolute if relative
                    if url.startswith('/'):
                        url = self.base_url + url
                    elif not url.startswith('http'):
                        url = f"{self.base_url}/{url}"

                    # Determine language
                    language = 'en'
                    auto_generated = False

                    if any(term in description.lower() for term in ['chinese', '中文', 'zh']):
                        language = 'zh'
                    elif any(term in description.lower() for term in ['english', 'en']):
                        language = 'en'

                    if any(term in description.lower() for term in ['auto', 'automatic', 'generated']):
                        auto_generated = True

                    subtitles.append({
                        'url': url,
                        'language': language,
                        'description': description.strip(),
                        'auto_generated': auto_generated
                    })

            # Method 3: Look for any links containing subtitle-related keywords
            if not subtitles:
                # More aggressive pattern to find any subtitle-related links
                general_pattern = r'href="([^"]*)"[^>]*>([^<]*(?:subtitle|字幕|srt|vtt|txt)[^<]*)'
                matches = re.findall(general_pattern, html_content, re.IGNORECASE)

                for url, description in matches:
                    if url.startswith('/'):
                        url = self.base_url + url
                    elif not url.startswith('http'):
                        url = f"{self.base_url}/{url}"

                    subtitles.append({
                        'url': url,
                        'language': 'en',
                        'description': description.strip(),
                        'auto_generated': False
                    })

            logger.debug(f"Found {len(subtitles)} subtitle links")
            for sub in subtitles:
                logger.debug(f"Subtitle: {sub['description']} -> {sub['url']}")

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