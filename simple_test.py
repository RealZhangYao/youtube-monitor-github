#!/usr/bin/env python3
"""
Simple test for DownSub.com subtitle fetching.
"""

import os
import sys
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_downsub_direct():
    """Test DownSub.com directly with the video URL."""
    video_id = 'zsTLDSibZnE'
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    logger.info(f"🧪 Testing DownSub.com with video: {video_id}")

    # Create session with proper headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    try:
        # Method 1: Direct URL construction (like you showed)
        encoded_url = urllib.parse.quote(video_url, safe='')
        downsub_url = f"https://downsub.com/?url={encoded_url}"

        logger.info(f"📍 Accessing: {downsub_url}")

        response = session.get(downsub_url, timeout=30)
        logger.info(f"🌐 HTTP Status: {response.status_code}")

        if response.status_code == 200:
            # Save the response for analysis
            with open('downsub_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info("💾 Response saved to 'downsub_response.html'")

            # Parse for subtitle links
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for download links
            download_links = []

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)

                # Check if this looks like a subtitle file
                if any(ext in href.lower() for ext in ['.srt', '.vtt', '.txt', '.sbv']):
                    download_links.append({
                        'url': href,
                        'text': text,
                        'type': 'subtitle_file'
                    })

                # Check if text mentions download or subtitle
                elif any(word in text.lower() for word in ['download', 'subtitle', '字幕', '下载']):
                    download_links.append({
                        'url': href,
                        'text': text,
                        'type': 'download_link'
                    })

            if download_links:
                logger.info(f"✅ Found {len(download_links)} potential subtitle links:")
                for i, link in enumerate(download_links, 1):
                    logger.info(f"  {i}. {link['text']} -> {link['url']} ({link['type']})")

                # Try to download the first subtitle link
                first_link = download_links[0]
                subtitle_url = first_link['url']

                # Make URL absolute if needed
                if subtitle_url.startswith('/'):
                    subtitle_url = f"https://downsub.com{subtitle_url}"
                elif not subtitle_url.startswith('http'):
                    subtitle_url = f"https://downsub.com/{subtitle_url}"

                logger.info(f"📥 Trying to download from: {subtitle_url}")

                subtitle_response = session.get(subtitle_url, timeout=30)
                if subtitle_response.status_code == 200:
                    content = subtitle_response.text[:500]  # First 500 chars
                    logger.info(f"✅ Downloaded subtitle content preview:")
                    logger.info(f"📄 Content: {content}...")

                    # Save the subtitle
                    with open('downloaded_subtitle.txt', 'w', encoding='utf-8') as f:
                        f.write(subtitle_response.text)
                    logger.info("💾 Subtitle saved to 'downloaded_subtitle.txt'")

                    return True
                else:
                    logger.error(f"❌ Failed to download subtitle: {subtitle_response.status_code}")

            else:
                logger.warning("⚠️  No subtitle links found in the page")

                # Let's see what the page contains
                content_lower = response.text.lower()
                has_error = any(term in content_lower for term in ['error', 'not found', 'unavailable'])
                has_subtitles = any(term in content_lower for term in ['subtitle', 'srt', 'vtt', 'txt'])

                logger.info(f"🔍 Page analysis:")
                logger.info(f"  Contains error terms: {has_error}")
                logger.info(f"  Contains subtitle terms: {has_subtitles}")

                # Print first 1000 characters of response for debugging
                logger.debug(f"📄 First 1000 chars of response:")
                logger.debug(response.text[:1000])

        else:
            logger.error(f"❌ Failed to access DownSub.com: {response.status_code}")

        return False

    except Exception as e:
        logger.error(f"💥 Error testing DownSub: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🚀 Starting DownSub.com test...")

    success = test_downsub_direct()

    if success:
        logger.info("🎉 DownSub test completed successfully!")
    else:
        logger.error("💥 DownSub test failed")


if __name__ == '__main__':
    main()