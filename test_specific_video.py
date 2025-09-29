#!/usr/bin/env python3
"""
Test script for specific video subtitle fetching with DownSub.com.

This script tests the DownSub.com integration for the video that was reported to have subtitles.
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from downsub_fetcher import DownSubFetcher
from transcript_fetcher import TranscriptFetcher

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG to see detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_specific_video():
    """Test the specific video that should have subtitles."""
    video_id = 'zsTLDSibZnE'
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    logger.info(f"Testing video: {video_id}")
    logger.info(f"Video URL: {video_url}")

    # Test DownSub fetcher
    logger.info("=== Testing DownSub Fetcher ===")
    downsub_fetcher = DownSubFetcher()

    transcript, language = downsub_fetcher.fetch_transcript(video_id)

    if transcript:
        logger.info(f"✅ DownSub SUCCESS: Found transcript in {language}")
        logger.info(f"📄 Transcript length: {len(transcript)} characters")
        logger.info(f"📝 Preview: {transcript[:300]}...")
        return True
    else:
        logger.error("❌ DownSub FAILED: No transcript found")

    # Test original fetcher for comparison
    logger.info("\n=== Testing Original Fetcher ===")
    original_fetcher = TranscriptFetcher()

    transcript, language = original_fetcher.fetch_transcript(video_id)

    if transcript:
        logger.info(f"✅ Original SUCCESS: Found transcript in {language}")
        logger.info(f"📄 Transcript length: {len(transcript)} characters")
        logger.info(f"📝 Preview: {transcript[:300]}...")
        return True
    else:
        logger.error("❌ Original FAILED: No transcript found")

    return False


def test_downsub_url_construction():
    """Test the URL construction for DownSub.com."""
    video_id = 'zsTLDSibZnE'
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    import urllib.parse
    encoded_url = urllib.parse.quote(video_url, safe='')
    downsub_url = f"https://downsub.com/?url={encoded_url}"

    logger.info(f"📍 DownSub URL that should work: {downsub_url}")

    # Test if we can access this URL
    import requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        response = session.get(downsub_url, timeout=30)
        logger.info(f"🌐 HTTP Status: {response.status_code}")

        if response.status_code == 200:
            # Check if the response contains subtitle-related content
            content = response.text.lower()

            has_download = 'download' in content
            has_subtitle = any(term in content for term in ['subtitle', 'srt', 'vtt', 'txt'])
            has_error = any(term in content for term in ['error', 'not found', 'unavailable'])

            logger.info(f"📥 Contains 'download': {has_download}")
            logger.info(f"📄 Contains subtitle terms: {has_subtitle}")
            logger.info(f"❌ Contains error terms: {has_error}")

            # Save response for debugging
            with open('downsub_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info("💾 Response saved to 'downsub_response.html' for debugging")

        return response.status_code == 200

    except Exception as e:
        logger.error(f"🚫 Failed to access DownSub URL: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🧪 Testing specific video subtitle fetching...")

    # Test 1: URL construction and access
    logger.info("\n1️⃣ Testing DownSub URL construction...")
    url_test = test_downsub_url_construction()

    # Test 2: Subtitle fetching
    logger.info("\n2️⃣ Testing subtitle fetching...")
    subtitle_test = test_specific_video()

    # Summary
    logger.info("\n📊 Test Summary:")
    logger.info(f"URL Access: {'✅ PASS' if url_test else '❌ FAIL'}")
    logger.info(f"Subtitle Fetch: {'✅ PASS' if subtitle_test else '❌ FAIL'}")

    if url_test and not subtitle_test:
        logger.warning("⚠️  URL access works but subtitle parsing failed. Check 'downsub_response.html'")
    elif subtitle_test:
        logger.info("🎉 Subtitle fetching works!")
    else:
        logger.error("💥 Both tests failed. Check network and DownSub.com availability.")


if __name__ == '__main__':
    main()