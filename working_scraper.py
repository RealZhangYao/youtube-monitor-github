#!/usr/bin/env python3
"""
Test the working DownSub fetcher implementation
"""

import os
import sys
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from downsub_fetcher import DownSubFetcher

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_downsub_with_specific_video():
    """Test DownSub fetcher with the specific video that should have subtitles"""

    logger.info("🚀 Testing DownSub fetcher with working implementation...")

    # Initialize the fetcher
    fetcher = DownSubFetcher()

    # Test with the video ID that the user confirmed has subtitles
    test_video_id = 'zsTLDSibZnE'

    logger.info(f"📺 Testing with video ID: {test_video_id}")
    logger.info(f"🔗 YouTube URL: https://www.youtube.com/watch?v={test_video_id}")
    logger.info(f"🌐 DownSub URL: https://downsub.com/?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{test_video_id}")

    # Fetch transcript
    transcript, language = fetcher.fetch_transcript(test_video_id)

    # Results
    if transcript:
        logger.info("🎉 SUCCESS: Transcript fetched successfully!")
        logger.info(f"📝 Language: {language}")
        logger.info(f"📏 Length: {len(transcript)} characters")
        logger.info(f"📄 Preview: {transcript[:200]}...")

        # Save transcript to file for verification
        with open(f'transcript_{test_video_id}.txt', 'w', encoding='utf-8') as f:
            f.write(transcript)
        logger.info(f"💾 Transcript saved to: transcript_{test_video_id}.txt")

        return True
    else:
        logger.error("❌ FAILED: No transcript found")
        logger.info("💡 This could mean:")
        logger.info("   - The video doesn't have subtitles available")
        logger.info("   - DownSub.com can't access this video")
        logger.info("   - Our API implementation needs further refinement")

        return False


def test_multiple_videos():
    """Test with multiple videos to verify functionality"""

    test_videos = [
        'zsTLDSibZnE',  # The video user confirmed has subtitles
        'dQw4w9WgXcQ',  # Never Gonna Give You Up (popular video)
        'jNQXAC9IVRw',  # Another popular video
    ]

    fetcher = DownSubFetcher()
    results = []

    for video_id in test_videos:
        logger.info(f"\n🧪 Testing video: {video_id}")
        transcript, language = fetcher.fetch_transcript(video_id)

        result = {
            'video_id': video_id,
            'success': transcript is not None,
            'language': language,
            'length': len(transcript) if transcript else 0
        }
        results.append(result)

        if transcript:
            logger.info(f"✅ Success: {len(transcript)} chars in {language}")
        else:
            logger.info("❌ Failed")

    # Summary
    logger.info("\n📊 Test Summary:")
    success_count = sum(1 for r in results if r['success'])
    logger.info(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

    for result in results:
        status = "✅" if result['success'] else "❌"
        logger.info(f"  {status} {result['video_id']}: {result['length']} chars ({result['language']})")

    return results


def main():
    """Main test function"""
    logger.info("🎯 Starting DownSub fetcher tests...")

    # Test 1: Specific video that should work
    logger.info("\n1️⃣ Testing specific video with confirmed subtitles...")
    success = test_downsub_with_specific_video()

    if success:
        # Test 2: Multiple videos
        logger.info("\n2️⃣ Testing multiple videos...")
        results = test_multiple_videos()

        logger.info("\n🎉 DownSub fetcher implementation appears to be working!")
    else:
        logger.warning("\n⚠️ DownSub fetcher needs further investigation")
        logger.info("💡 Recommendations:")
        logger.info("   1. Check if the video actually has subtitles available")
        logger.info("   2. Verify DownSub.com is accessible")
        logger.info("   3. Consider using YouTube Transcript API as primary method")


if __name__ == '__main__':
    main()