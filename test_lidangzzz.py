#!/usr/bin/env python3
"""
Test script for @lidangzzz channel monitoring with DownSub.com integration.

This script tests the new functionality without requiring full environment setup.
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_client import YouTubeClient
from downsub_fetcher import DownSubFetcher
from transcript_fetcher import TranscriptFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_youtube_api():
    """Test YouTube API functionality."""
    logger.info("=== Testing YouTube API ===")

    # You need to set your YouTube API key here
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        logger.error("Please set YOUTUBE_API_KEY environment variable")
        return False

    try:
        client = YouTubeClient(api_key)

        # Test 1: Get channel ID by username
        logger.info("Test 1: Getting channel ID for @lidangzzz")
        channel_id = client.get_channel_id_by_username('lidangzzz')
        if channel_id:
            logger.info(f"✓ Found channel ID: {channel_id}")
        else:
            logger.error("✗ Could not find channel ID for @lidangzzz")
            return False

        # Test 2: Get channel info
        logger.info("Test 2: Getting channel information")
        channel_info = client.get_channel_info(channel_id)
        if channel_info:
            logger.info(f"✓ Channel: {channel_info['title']}")
            logger.info(f"  Uploads playlist: {channel_info['uploads_playlist_id']}")
        else:
            logger.error("✗ Could not get channel information")
            return False

        # Test 3: Get latest videos
        logger.info("Test 3: Getting latest videos (limit 2)")
        videos = client.get_latest_videos(channel_id, max_results=2)
        if videos:
            logger.info(f"✓ Found {len(videos)} videos:")
            for i, video in enumerate(videos, 1):
                logger.info(f"  {i}. {video['title']}")
                logger.info(f"     Video ID: {video['id']}")
                logger.info(f"     Published: {video['published_at']}")
                logger.info(f"     URL: {video['url']}")
        else:
            logger.error("✗ No videos found")
            return False

        return True, videos[0] if videos else None

    except Exception as e:
        logger.error(f"YouTube API test failed: {e}")
        return False, None


def test_downsub_fetcher(test_video_id='dQw4w9WgXcQ'):
    """Test DownSub.com transcript fetcher."""
    logger.info("=== Testing DownSub.com Fetcher ===")

    try:
        fetcher = DownSubFetcher()

        logger.info(f"Testing with video ID: {test_video_id}")
        transcript, language = fetcher.fetch_transcript(test_video_id)

        if transcript:
            logger.info(f"✓ Successfully fetched transcript in {language}")
            logger.info(f"  Length: {len(transcript)} characters")
            logger.info(f"  Preview: {transcript[:200]}...")
            return True
        else:
            logger.warning("✗ No transcript fetched")
            return False

    except Exception as e:
        logger.error(f"DownSub fetcher test failed: {e}")
        return False


def test_original_fetcher(test_video_id='dQw4w9WgXcQ'):
    """Test original transcript fetcher for comparison."""
    logger.info("=== Testing Original Transcript Fetcher ===")

    try:
        fetcher = TranscriptFetcher()

        logger.info(f"Testing with video ID: {test_video_id}")
        transcript, language = fetcher.fetch_transcript(test_video_id)

        if transcript:
            logger.info(f"✓ Successfully fetched transcript in {language}")
            logger.info(f"  Length: {len(transcript)} characters")
            logger.info(f"  Preview: {transcript[:200]}...")
            return True
        else:
            logger.warning("✗ No transcript fetched")
            return False

    except Exception as e:
        logger.error(f"Original fetcher test failed: {e}")
        return False


def compare_fetchers(video_id):
    """Compare both transcript fetchers."""
    logger.info("=== Comparing Transcript Fetchers ===")

    # Test DownSub
    logger.info("Testing DownSub fetcher...")
    downsub_fetcher = DownSubFetcher()
    downsub_transcript, downsub_lang = downsub_fetcher.fetch_transcript(video_id)

    # Test Original
    logger.info("Testing original fetcher...")
    original_fetcher = TranscriptFetcher()
    original_transcript, original_lang = original_fetcher.fetch_transcript(video_id)

    # Compare results
    logger.info("=== Comparison Results ===")
    logger.info(f"DownSub: {'Success' if downsub_transcript else 'Failed'} ({downsub_lang})")
    logger.info(f"Original: {'Success' if original_transcript else 'Failed'} ({original_lang})")

    if downsub_transcript and original_transcript:
        logger.info(f"DownSub length: {len(downsub_transcript)}")
        logger.info(f"Original length: {len(original_transcript)}")


def test_get_latest_mode():
    """Test GET_LATEST mode functionality."""
    logger.info("=== Testing GET_LATEST Mode ===")

    # Set environment variable for testing
    os.environ['GET_LATEST'] = 'true'
    os.environ['TARGET_USERNAME'] = 'lidangzzz'

    # You would need other required environment variables set
    required_vars = ['YOUTUBE_API_KEY', 'GEMINI_API_KEY', 'GMAIL_USER', 'GMAIL_APP_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        logger.warning(f"Cannot test GET_LATEST mode - missing environment variables: {missing_vars}")
        return False

    try:
        # Import and run main function
        from main import main as run_main
        logger.info("Running main program in GET_LATEST mode...")
        run_main()
        logger.info("✓ GET_LATEST mode executed successfully")
        return True
    except Exception as e:
        logger.error(f"✗ GET_LATEST mode failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🚀 Starting @lidangzzz monitoring tests...")

    # Test 1: YouTube API
    youtube_success, latest_video = test_youtube_api()
    if not youtube_success:
        logger.error("YouTube API tests failed")
        return

    # Test 2: DownSub fetcher with a known video
    downsub_success = test_downsub_fetcher()

    # Test 3: Original fetcher for comparison
    original_success = test_original_fetcher()

    # Test 4: Compare both fetchers with latest video if available
    if latest_video:
        logger.info(f"\n=== Testing with latest video from @lidangzzz ===")
        logger.info(f"Video: {latest_video['title']}")
        compare_fetchers(latest_video['id'])

    # Test 5: GET_LATEST mode (if environment is set up)
    get_latest_success = test_get_latest_mode()

    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"YouTube API: {'✓ PASS' if youtube_success else '✗ FAIL'}")
    logger.info(f"DownSub Fetcher: {'✓ PASS' if downsub_success else '✗ FAIL'}")
    logger.info(f"Original Fetcher: {'✓ PASS' if original_success else '✗ FAIL'}")
    logger.info(f"GET_LATEST Mode: {'✓ PASS' if get_latest_success else '⚠ SKIP (missing env vars)'}")

    if youtube_success and downsub_success:
        logger.info("\n🎉 All core tests passed! The system is ready to monitor @lidangzzz")
        if get_latest_success:
            logger.info("💡 GET_LATEST mode is also working - you can use it to always get the newest video!")
    else:
        logger.warning("\n⚠️  Some tests failed. Check the logs above for details.")


if __name__ == '__main__':
    main()