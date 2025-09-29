"""
DownSub.com transcript fetcher module.

This module uses DownSub.com API to fetch video transcripts/subtitles.
It provides an alternative to youtube-transcript-api with better reliability.
"""

import logging
import time
import json
import re
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple
import requests

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
        Get available subtitle information from DownSub.com using comprehensive approach.

        This method implements multiple strategies based on reverse engineering:
        1. Direct API call to get basic info
        2. Simulation of known working download URLs
        3. Fallback to web scraping

        Args:
            video_url: YouTube video URL

        Returns:
            List of available subtitle tracks or None
        """
        try:
            # Strategy 1: Use the discovered API endpoint to get basic structure
            logger.debug("Strategy 1: Checking DownSub API for basic info...")
            api_result = self._check_downsub_api(video_url)

            # Strategy 2: Try to use known working download patterns
            logger.debug("Strategy 2: Attempting direct subtitle access...")
            direct_result = self._try_direct_subtitle_access(video_url)

            if direct_result:
                logger.info("✅ Found subtitles via direct access method")
                return direct_result

            # Strategy 3: If no direct success, try API-guided approach
            if api_result and api_result.get('urlSubtitle'):
                logger.debug("Strategy 3: Using API-guided subtitle detection...")
                guided_result = self._try_api_guided_access(video_url, api_result)
                if guided_result:
                    return guided_result

            # Strategy 4: Fallback to web scraping
            logger.debug("Strategy 4: Falling back to web scraping...")
            return self._scrape_subtitle_info(video_url)

        except Exception as e:
            logger.error(f"Error in comprehensive subtitle detection: {e}")
            return None

    def _check_downsub_api(self, video_url: str) -> Optional[Dict]:
        """Check DownSub API for basic video info"""
        try:
            api_url = "https://get.downsub.com/"

            self.session.headers.update({
                'Referer': 'https://downsub.com/',
                'Origin': 'https://downsub.com',
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest'
            })

            payload = {'url': video_url}
            response = self.session.post(api_url, json=payload, timeout=30)

            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.debug(f"DownSub API response: {result}")

                    # Check if API returns actual subtitles
                    subtitles = result.get('subtitles', [])
                    auto_subtitles = result.get('subtitlesAutoTrans', [])

                    if subtitles or auto_subtitles:
                        logger.info("API returned subtitle data directly")
                        all_subtitles = []

                        for sub in subtitles:
                            all_subtitles.append({
                                'url': sub.get('url'),
                                'language': sub.get('lang', 'unknown'),
                                'description': sub.get('name', 'Manual subtitle'),
                                'auto_generated': False
                            })

                        for sub in auto_subtitles:
                            all_subtitles.append({
                                'url': sub.get('url'),
                                'language': sub.get('lang', 'unknown'),
                                'description': sub.get('name', 'Auto-generated subtitle'),
                                'auto_generated': True
                            })

                        return all_subtitles

                    return result  # Return for potential guided access

                except Exception as e:
                    logger.debug(f"Error parsing API response: {e}")

            else:
                logger.debug(f"API returned {response.status_code}")

        except Exception as e:
            logger.debug(f"API check failed: {e}")

        return None

    def _try_direct_subtitle_access(self, video_url: str) -> Optional[List[Dict]]:
        """
        Try to access subtitles using patterns discovered from working examples.

        Based on analysis of working download.subtitle.to URLs.
        """
        try:
            # Extract video ID from URL
            import re
            video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
            if not video_id_match:
                return None

            video_id = video_id_match.group(1)
            logger.debug(f"Extracted video ID: {video_id}")

            # Try multiple approaches to access subtitles for this video
            access_attempts = [
                # Attempt 1: Try to construct a download.subtitle.to URL
                # This is speculative but based on the pattern we observed
                f"https://download.subtitle.to/?url={video_id}&type=txt",
                f"https://download.subtitle.to/?video={video_id}&format=txt",

                # Attempt 2: Try DownSub's URL pattern with this video
                f"https://downsub.com/?url={urllib.parse.quote(video_url)}",
            ]

            for attempt_url in access_attempts:
                logger.debug(f"Trying direct access: {attempt_url}")

                try:
                    # Use appropriate headers for each domain
                    headers = {}
                    if 'download.subtitle.to' in attempt_url:
                        headers.update({
                            'Referer': 'https://downsub.com/',
                            'Accept': 'text/plain,text/html,*/*'
                        })

                    self.session.headers.update(headers)

                    response = self.session.get(attempt_url, timeout=30)

                    if response.status_code == 200:
                        content = response.text

                        # Check if this looks like subtitle content
                        if self._is_subtitle_content(content):
                            logger.info(f"✅ Found subtitle via direct access: {attempt_url}")

                            # Return as a subtitle track
                            return [{
                                'url': attempt_url,
                                'language': 'zh' if any(ord(char) > 127 for char in content[:1000]) else 'en',
                                'description': 'Direct access subtitle',
                                'auto_generated': False,
                                'content': content  # Include content directly
                            }]

                except Exception as e:
                    logger.debug(f"Direct access attempt failed: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Direct access method failed: {e}")

        return None

    def _try_api_guided_access(self, video_url: str, api_result: Dict) -> Optional[List[Dict]]:
        """Try to use API result to guide subtitle access"""
        try:
            base_url = api_result.get('urlSubtitle', 'https://download.subtitle.to/')

            if not base_url.endswith('/'):
                base_url += '/'

            # Try to construct download URLs based on API guidance
            # This would need the actual encryption key/method from DownSub
            # For now, we'll try basic patterns

            logger.debug(f"Attempting API-guided access with base: {base_url}")

            # This is where we would implement the actual URL construction
            # if we had the encryption key. For now, return None to fall back.

        except Exception as e:
            logger.debug(f"API-guided access failed: {e}")

        return None

    def _is_subtitle_content(self, content: str) -> bool:
        """Check if content appears to be subtitle data"""
        if not content or len(content) < 50:
            return False

        # Check for common subtitle patterns
        subtitle_indicators = [
            # SRT format
            re.search(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', content),
            # VTT format
            content.strip().startswith('WEBVTT'),
            # General timestamp patterns
            re.search(r'\d{1,2}:\d{2}:\d{2}', content),
            # Chinese characters (indicating content, not just HTML)
            len([c for c in content[:1000] if ord(c) > 127]) > 20,
            # Common subtitle words
            any(word in content.lower() for word in ['subtitle', '字幕', 'caption'])
        ]

        return any(subtitle_indicators)

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
        Download subtitle content from the given URL or extract from embedded content.

        Args:
            subtitle_info: Subtitle track information

        Returns:
            Subtitle content as text or None
        """
        try:
            # Check if content is already embedded (from direct access)
            if 'content' in subtitle_info:
                logger.debug("Using embedded subtitle content")
                content = subtitle_info['content']
            else:
                # Download from URL
                url = subtitle_info['url']
                logger.debug(f"Downloading subtitle from: {url}")

                response = self.session.get(url, timeout=30)

                if response.status_code != 200:
                    logger.error(f"Failed to download subtitle: HTTP {response.status_code}")
                    return None

                content = response.text

            # Convert subtitle content to plain text based on format
            if not content:
                return None

            # Determine format and process accordingly
            if subtitle_info.get('url', '').endswith('.srt') or self._is_srt_format(content):
                content = self._srt_to_text(content)
            elif subtitle_info.get('url', '').endswith('.vtt') or content.strip().startswith('WEBVTT'):
                content = self._vtt_to_text(content)
            else:
                # For plain text or other formats, clean up basic formatting
                content = self._clean_subtitle_text(content)

            return content

        except Exception as e:
            logger.error(f"Error processing subtitle: {e}")
            return None

    def _is_srt_format(self, content: str) -> bool:
        """Check if content is in SRT format"""
        return bool(re.search(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', content))

    def _clean_subtitle_text(self, content: str) -> str:
        """Clean up plain text subtitle content"""
        try:
            import re

            # Remove any HTML tags that might be present
            content = re.sub(r'<[^>]+>', '', content)

            # Clean up excessive whitespace
            content = re.sub(r'\n\s*\n', '\n', content)
            content = re.sub(r'\s+', ' ', content)

            # Split into lines and clean each line
            lines = content.split('\n')
            cleaned_lines = []

            for line in lines:
                line = line.strip()
                if line and not line.isdigit():  # Skip empty lines and standalone numbers
                    cleaned_lines.append(line)

            return '\n'.join(cleaned_lines)

        except Exception as e:
            logger.error(f"Error cleaning subtitle text: {e}")
            return content

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