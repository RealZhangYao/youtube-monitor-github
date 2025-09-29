#!/usr/bin/env python3
"""
Final DownSub.com scraper that mimics browser behavior precisely
"""

import requests
import re
import json
import logging
import time
from urllib.parse import quote, unquote
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def decode_imgproxy_url(imgproxy_url):
    """Decode imgproxy-style URLs that might contain base64 encoded URLs"""
    try:
        # Extract the base64 part from URLs like imgproxy.nanxiongnandi.com/.../.../aHR0cHM6Ly9pbWcu/bmFueGlvbmduYW5k/aS5jb20vMjAyNTA5/L1BpZW56YUl0YWx5/LmpwZw.jpg
        parts = imgproxy_url.split('/')
        base64_parts = []

        # Look for parts that look like base64
        collect_base64 = False
        for part in parts:
            # Skip parameters like w:800, h:600
            if part.startswith('w:') or part.startswith('h:'):
                collect_base64 = True
                continue

            if collect_base64 and part:
                # Remove file extensions
                clean_part = re.sub(r'\.(jpg|jpeg|png|webp)$', '', part)
                if clean_part:
                    base64_parts.append(clean_part)

        if not base64_parts:
            return None

        # Join the base64 parts
        combined_base64 = ''.join(base64_parts)

        # Add padding if needed
        missing_padding = len(combined_base64) % 4
        if missing_padding:
            combined_base64 += '=' * (4 - missing_padding)

        # Decode
        decoded_url = base64.b64decode(combined_base64).decode('utf-8')

        # Check if it's a valid URL
        if decoded_url.startswith('http'):
            return decoded_url

    except Exception as e:
        logger.debug(f"Error decoding imgproxy URL: {e}")

    return None


def try_downsub_direct_access():
    """Try accessing DownSub.com directly with exact browser simulation"""

    session = requests.Session()

    # Set exact browser headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })

    test_video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'

    # Try the exact URL format the user showed
    try:
        logger.info("🔗 Trying exact URL format from user...")
        encoded_url = quote(test_video_url, safe='')
        direct_url = f"https://downsub.com/?url={encoded_url}"

        logger.info(f"Accessing: {direct_url}")

        response = session.get(direct_url, timeout=30)
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Content length: {len(response.text)}")

        if response.status_code == 200:
            # Save the response for analysis
            with open('downsub_direct_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Look for subtitle download links in the response
            subtitle_patterns = [
                r'href="([^"]*\.(?:srt|vtt|txt|sbv)[^"]*)"',
                r'href="([^"]*download[^"]*)"[^>]*>[^<]*(?:subtitle|字幕|download|下载)',
                r'<a[^>]*href="([^"]*)"[^>]*>[^<]*(?:Download|下载|subtitle|字幕)',
                # Look for any URLs that might be imgproxy-encoded
                r'href="([^"]*imgproxy[^"]*)"',
                r'src="([^"]*imgproxy[^"]*)"',
            ]

            found_links = []
            for pattern in subtitle_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    # Try to decode if it looks like an imgproxy URL
                    if 'imgproxy' in match:
                        decoded = decode_imgproxy_url(match)
                        if decoded:
                            logger.info(f"🔍 Decoded imgproxy URL: {match} -> {decoded}")
                            found_links.append(decoded)
                        else:
                            found_links.append(match)
                    else:
                        found_links.append(match)

            if found_links:
                logger.info(f"🎉 Found {len(found_links)} potential subtitle links:")
                for i, link in enumerate(found_links, 1):
                    logger.info(f"  {i}. {link}")

                    # Try to download the first few links
                    if i <= 3:
                        try_download_subtitle(session, link, i)
            else:
                logger.warning("❌ No subtitle links found in direct response")

                # Look for any JavaScript that might load content dynamically
                js_patterns = [
                    r'<script[^>]*src="([^"]*)"',
                    r'fetch\s*\(\s*[\'"`]([^\'"`]*)[\'"`]',
                    r'axios\.\w+\s*\(\s*[\'"`]([^\'"`]*)[\'"`]',
                ]

                for pattern in js_patterns:
                    matches = re.findall(pattern, response.text)
                    for match in matches:
                        logger.info(f"📄 Found JS/API reference: {match}")

        else:
            logger.error(f"❌ Failed to access direct URL: {response.status_code}")

    except Exception as e:
        logger.error(f"💥 Error in direct access: {e}")


def try_download_subtitle(session, url, index):
    """Try to download subtitle from a given URL"""
    try:
        logger.info(f"📥 Trying to download subtitle {index}: {url}")

        # Make URL absolute if needed
        if url.startswith('/'):
            url = f"https://downsub.com{url}"
        elif not url.startswith('http'):
            url = f"https://downsub.com/{url}"

        # Update headers for subtitle download
        session.headers.update({
            'Referer': 'https://downsub.com/',
            'Accept': 'text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })

        response = session.get(url, timeout=30)
        logger.info(f"  Status: {response.status_code}")
        logger.info(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
        logger.info(f"  Content length: {len(response.text)}")

        if response.status_code == 200:
            # Check if it looks like subtitle content
            content = response.text.strip()

            # SRT format check
            if re.search(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', content):
                logger.info("  ✅ Looks like SRT format!")
                with open(f'subtitle_{index}.srt', 'w', encoding='utf-8') as f:
                    f.write(content)
                return content

            # VTT format check
            elif content.startswith('WEBVTT'):
                logger.info("  ✅ Looks like VTT format!")
                with open(f'subtitle_{index}.vtt', 'w', encoding='utf-8') as f:
                    f.write(content)
                return content

            # Plain text check
            elif len(content) > 50 and not content.startswith('<'):
                logger.info("  ✅ Looks like plain text subtitle!")
                with open(f'subtitle_{index}.txt', 'w', encoding='utf-8') as f:
                    f.write(content)
                return content

            else:
                logger.info(f"  ❓ Content doesn't look like subtitle: {content[:100]}...")

        else:
            logger.warning(f"  ❌ Failed to download: {response.status_code}")

    except Exception as e:
        logger.error(f"  💥 Download error: {e}")

    return None


def try_api_with_cookies():
    """Try API calls with cookies from main site"""

    session = requests.Session()

    # First, visit the main site to get cookies
    logger.info("🍪 Getting cookies from main site...")
    response = session.get('https://downsub.com', timeout=30)
    logger.info(f"Cookies: {list(session.cookies.keys())}")

    # Now try API calls with cookies
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://downsub.com/',
        'Origin': 'https://downsub.com',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest'
    })

    test_video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'

    # Try different payload formats based on what might work
    payloads = [
        {'url': test_video_url},
        {'link': test_video_url},
        {'video_url': test_video_url},
        {'supported_sites': test_video_url},
        {
            'url': test_video_url,
            'action': 'download',
            'type': 'youtube'
        }
    ]

    for i, payload in enumerate(payloads, 1):
        logger.info(f"🧪 Testing API payload {i}: {payload}")

        try:
            response = session.post('https://get.downsub.com/', json=payload, timeout=30)
            logger.info(f"  Status: {response.status_code}")
            logger.info(f"  Content: {response.text[:200]}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('subtitles') and len(data['subtitles']) > 0:
                        logger.info("🎉 Found subtitles in API response!")
                        logger.info(f"Subtitles: {json.dumps(data['subtitles'], indent=2)}")
                        return data
                    else:
                        logger.info("  ❌ No subtitles in response")
                except:
                    pass

        except Exception as e:
            logger.warning(f"  ❌ API call failed: {e}")

        time.sleep(1)

    return None


def main():
    """Main function"""
    logger.info("🚀 Starting final DownSub.com scraper...")

    # Method 1: Direct access with exact URL format
    logger.info("\n1️⃣ Trying direct access with exact URL format...")
    try_downsub_direct_access()

    # Method 2: API calls with cookies
    logger.info("\n2️⃣ Trying API calls with cookies...")
    api_result = try_api_with_cookies()

    # Summary
    logger.info("\n📊 Final scraper summary:")
    if api_result:
        logger.info("🎉 Successfully found subtitles via API!")
    else:
        logger.warning("⚠️ No subtitles found via API - check saved HTML files")
        logger.info("💡 Next steps: analyze downsub_direct_response.html for client-side JavaScript patterns")


if __name__ == '__main__':
    main()