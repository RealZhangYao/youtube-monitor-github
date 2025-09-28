"""
YouTube Monitor - Main entry point for GitHub Actions
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_client import YouTubeClient
from transcript_fetcher import TranscriptFetcher
from ai_summarizer import AISummarizer
from email_sender import EmailSender
from data_store import DataStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function for YouTube monitoring."""
    logger.info("YouTube Monitor started")
    
    # Configuration
    config = {
        'youtube_api_key': os.environ.get('YOUTUBE_API_KEY'),
        'gemini_api_key': os.environ.get('GEMINI_API_KEY'),
        'gmail_user': os.environ.get('GMAIL_USER'),
        'gmail_password': os.environ.get('GMAIL_APP_PASSWORD'),
        'recipient_email': os.environ.get('RECIPIENT_EMAIL'),
        'channels': os.environ.get('CHANNELS_TO_MONITOR', '').split(','),
        'test_mode': os.environ.get('TEST_MODE', 'false').lower() == 'true'
    }
    
    # Validate configuration
    required_keys = ['youtube_api_key', 'gemini_api_key', 'gmail_user', 
                     'gmail_password', 'recipient_email']
    
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logger.error(f"Missing required configuration: {', '.join(missing_keys)}")
        sys.exit(1)
    
    if not config['channels'] or config['channels'] == ['']:
        logger.error("No channels to monitor")
        sys.exit(1)
    
    # Initialize components
    youtube_client = YouTubeClient(config['youtube_api_key'])
    transcript_fetcher = TranscriptFetcher()
    ai_summarizer = AISummarizer(config['gemini_api_key'])
    email_sender = EmailSender(config['gmail_user'], config['gmail_password'])
    data_store = DataStore('data')
    
    # Test mode
    if config['test_mode']:
        logger.info("Running in test mode")
        test_components(youtube_client, transcript_fetcher, ai_summarizer, 
                       email_sender, data_store)
        return
    
    # Process each channel
    total_new_videos = 0
    all_results = []
    
    for channel_id in config['channels']:
        if not channel_id.strip():
            continue
            
        logger.info(f"Processing channel: {channel_id}")
        
        try:
            result = process_channel(
                channel_id.strip(),
                youtube_client,
                transcript_fetcher,
                ai_summarizer,
                email_sender,
                data_store,
                config['recipient_email']
            )
            
            all_results.append(result)
            total_new_videos += result['new_videos_count']
            
        except Exception as e:
            logger.error(f"Error processing channel {channel_id}: {e}")
            all_results.append({
                'channel_id': channel_id,
                'error': str(e),
                'new_videos_count': 0
            })
    
    # Summary
    logger.info(f"Processing complete. Total new videos: {total_new_videos}")
    logger.info(f"Results: {json.dumps(all_results, indent=2)}")
    
    # Save summary
    summary_file = Path('data/last_run_summary.json')
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    summary_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_new_videos': total_new_videos,
        'channels_processed': len(config['channels']),
        'results': all_results
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    # Send summary email (always, even if no new videos)
    logger.info("Sending summary email...")
    email_sent = email_sender.send_summary_email(
        config['recipient_email'],
        summary_data
    )
    
    if email_sent:
        logger.info("Summary email sent successfully")
    else:
        logger.error("Failed to send summary email")


def process_channel(channel_id, youtube_client, transcript_fetcher, 
                   ai_summarizer, email_sender, data_store, recipient_email):
    """Process a single YouTube channel."""
    result = {
        'channel_id': channel_id,
        'channel_name': 'Unknown',
        'new_videos_count': 0,
        'processed_videos': []
    }
    
    # Get channel info
    channel_info = youtube_client.get_channel_info(channel_id)
    if not channel_info:
        logger.error(f"Channel not found: {channel_id}")
        result['error'] = 'Channel not found'
        return result
    
    result['channel_name'] = channel_info['title']
    
    # Get processed videos
    processed_videos = data_store.get_processed_videos(channel_id)
    processed_video_ids = {v['video_id'] for v in processed_videos}
    
    # Get latest videos
    latest_videos = youtube_client.get_latest_videos(channel_id, max_results=10)
    
    # Process new videos
    for video in latest_videos:
        if video['id'] in processed_video_ids:
            logger.info(f"Video already processed: {video['title']}")
            continue
        
        logger.info(f"Processing new video: {video['title']}")
        
        # Get transcript
        transcript, language = transcript_fetcher.fetch_transcript(video['id'])
        
        if not transcript:
            logger.warning(f"No transcript available for: {video['title']}")
            
            # Generate basic summary without transcript
            basic_summary = f"""
新视频通知

标题: {video['title']}
频道: {video['channel_title']}
时长: {video['duration']}
观看次数: {video['view_count']:,} 次
发布时间: {video['published_at']}

链接: {video['url']}

注：该视频未开启字幕功能，无法生成内容摘要。
"""
            
            # Send email notification with basic info
            email_sent = email_sender.send_video_notification(
                recipient_email,
                video,
                basic_summary
            )
            
            if not email_sent:
                logger.error(f"Failed to send email for: {video['title']}")
            
            # Mark as processed
            data_store.mark_video_processed(
                channel_id, 
                video['id'], 
                video,
                summary=basic_summary,
                email_sent=email_sent
            )
            
            result['new_videos_count'] += 1
            result['processed_videos'].append({
                'video_id': video['id'],
                'title': video['title'],
                'summary': '无字幕，仅包含基本信息'
            })
            continue
        
        # Save transcript
        data_store.save_transcript(channel_id, video['id'], transcript, language)
        
        # Generate summary
        summary = ai_summarizer.generate_summary(video, transcript)
        
        if not summary:
            summary = f"Unable to generate summary for: {video['title']}"
        
        # Send email notification
        email_sent = email_sender.send_video_notification(
            recipient_email,
            video,
            summary
        )
        
        if not email_sent:
            logger.error(f"Failed to send email for: {video['title']}")
        
        # Mark as processed
        data_store.mark_video_processed(
            channel_id, 
            video['id'], 
            video,
            summary=summary,
            email_sent=email_sent
        )
        
        result['new_videos_count'] += 1
        result['processed_videos'].append({
            'video_id': video['id'],
            'title': video['title'],
            'summary': summary[:200] + '...' if len(summary) > 200 else summary
        })
    
    return result


def test_components(youtube_client, transcript_fetcher, ai_summarizer, 
                   email_sender, data_store):
    """Test all components."""
    logger.info("Testing components...")
    
    results = {
        'youtube_api': False,
        'transcript_api': False,
        'gemini_api': False,
        'gmail_smtp': False,
        'data_store': False
    }
    
    # Test YouTube API
    try:
        results['youtube_api'] = youtube_client.check_api_quota()
        logger.info(f"YouTube API: {'OK' if results['youtube_api'] else 'FAILED'}")
    except Exception as e:
        logger.error(f"YouTube API test failed: {e}")
    
    # Test Transcript API
    try:
        # Test with a known video
        transcript, _ = transcript_fetcher.fetch_transcript('dQw4w9WgXcQ')
        results['transcript_api'] = transcript is not None
        logger.info(f"Transcript API: {'OK' if results['transcript_api'] else 'FAILED'}")
    except Exception as e:
        logger.error(f"Transcript API test failed: {e}")
    
    # Test Gemini API
    try:
        results['gemini_api'] = ai_summarizer.test_connection()
        logger.info(f"Gemini API: {'OK' if results['gemini_api'] else 'FAILED'}")
    except Exception as e:
        logger.error(f"Gemini API test failed: {e}")
    
    # Test Gmail SMTP
    try:
        results['gmail_smtp'] = email_sender.test_connection()
        logger.info(f"Gmail SMTP: {'OK' if results['gmail_smtp'] else 'FAILED'}")
    except Exception as e:
        logger.error(f"Gmail SMTP test failed: {e}")
    
    # Test data store
    try:
        test_data = data_store.get_processed_videos('test_channel')
        results['data_store'] = True
        logger.info(f"Data Store: OK")
    except Exception as e:
        logger.error(f"Data Store test failed: {e}")
    
    # Summary
    all_passed = all(results.values())
    logger.info(f"All tests passed: {'YES' if all_passed else 'NO'}")
    
    # Save test results
    with open('data/test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results': results,
            'all_passed': all_passed
        }, f, indent=2)
    
    if not all_passed:
        sys.exit(1)


if __name__ == '__main__':
    main()