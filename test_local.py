#!/usr/bin/env python3
"""
Local test script for YouTube Monitor
Run this to test your configuration before deploying to GitHub Actions
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from youtube_client import YouTubeClient
        from transcript_fetcher import TranscriptFetcher
        from ai_summarizer import AISummarizer
        from email_sender import EmailSender
        from data_store import DataStore
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_environment():
    """Test that required environment variables are set."""
    print("\nChecking environment variables...")
    required_vars = [
        'YOUTUBE_API_KEY',
        'GEMINI_API_KEY', 
        'GMAIL_USER',
        'GMAIL_APP_PASSWORD',
        'RECIPIENT_EMAIL',
        'CHANNELS_TO_MONITOR'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'PASSWORD' in var:
                masked = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
                print(f"✓ {var}: {masked}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: Not set")
            all_set = False
    
    return all_set

def test_apis():
    """Test API connections."""
    print("\nTesting API connections...")
    
    # Only test if environment is set up
    if not all([os.environ.get('YOUTUBE_API_KEY'), 
                 os.environ.get('GEMINI_API_KEY'),
                 os.environ.get('GMAIL_USER')]):
        print("⚠ Skipping API tests - environment not configured")
        return
    
    # Test YouTube API
    try:
        from youtube_client import YouTubeClient
        client = YouTubeClient(os.environ['YOUTUBE_API_KEY'])
        if client.check_api_quota():
            print("✓ YouTube API connection successful")
        else:
            print("✗ YouTube API connection failed")
    except Exception as e:
        print(f"✗ YouTube API error: {e}")
    
    # Test Gemini API
    try:
        from ai_summarizer import AISummarizer
        ai = AISummarizer(os.environ['GEMINI_API_KEY'])
        if ai.test_connection():
            print("✓ Gemini AI connection successful")
        else:
            print("✗ Gemini AI connection failed")
    except Exception as e:
        print(f"✗ Gemini AI error: {e}")
    
    # Test Gmail SMTP
    try:
        from email_sender import EmailSender
        email = EmailSender(os.environ['GMAIL_USER'], os.environ['GMAIL_APP_PASSWORD'])
        if email.test_connection():
            print("✓ Gmail SMTP connection successful")
        else:
            print("✗ Gmail SMTP connection failed")
    except Exception as e:
        print(f"✗ Gmail SMTP error: {e}")

def main():
    """Run all tests."""
    print("YouTube Monitor - Local Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\nPlease install required dependencies:")
        print("pip install -r requirements.txt")
        return
    
    # Test environment
    env_ok = test_environment()
    
    if not env_ok:
        print("\nTo set environment variables:")
        print("export YOUTUBE_API_KEY='your-key-here'")
        print("export GEMINI_API_KEY='your-key-here'")
        print("export GMAIL_USER='your-email@gmail.com'")
        print("export GMAIL_APP_PASSWORD='your-app-password'")
        print("export RECIPIENT_EMAIL='recipient@example.com'")
        print("export CHANNELS_TO_MONITOR='channel1,channel2'")
        print("\nOr create a .env file with these values")
        return
    
    # Test APIs
    test_apis()
    
    print("\n" + "=" * 40)
    print("Test complete!")
    print("\nIf all tests passed, you're ready to:")
    print("1. Commit and push to GitHub")
    print("2. Set up GitHub Secrets")
    print("3. Enable GitHub Actions")

if __name__ == '__main__':
    # Try to load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    main()