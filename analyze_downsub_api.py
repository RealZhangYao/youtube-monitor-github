#!/usr/bin/env python3
"""
逆向工程 DownSub.com 的 API 调用
"""

import requests
import re
import json
import logging
from urllib.parse import urljoin, urlparse
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_downsub_js():
    """分析 DownSub.com 的 JavaScript 文件来找到 API 端点"""

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    try:
        # 获取主页面来找到 JS 文件
        logger.info("📄 获取 DownSub.com 主页面...")
        response = session.get('https://downsub.com', timeout=30)

        if response.status_code != 200:
            logger.error(f"无法访问主页面: {response.status_code}")
            return None

        # 从 HTML 中提取 JavaScript 文件 URL
        js_files = re.findall(r'src=([\'"]?)([^\'">]*\.js)(?:\?[^\'"]*)?[\'"]?', response.text)

        logger.info(f"🔍 找到 {len(js_files)} 个 JavaScript 文件:")

        api_patterns = []

        for quote, js_file in js_files:
            if js_file.startswith('/'):
                js_url = f"https://downsub.com{js_file}"
            else:
                js_url = js_file

            logger.info(f"  📦 分析: {js_url}")

            try:
                js_response = session.get(js_url, timeout=30)
                if js_response.status_code == 200:
                    # 分析 JavaScript 代码
                    patterns = analyze_js_content(js_response.text, js_url)
                    api_patterns.extend(patterns)

            except Exception as e:
                logger.warning(f"⚠️  无法下载 {js_url}: {e}")

        return api_patterns

    except Exception as e:
        logger.error(f"💥 分析失败: {e}")
        return None


def analyze_js_content(js_content, js_url):
    """分析 JavaScript 内容来找到 API 调用"""

    patterns = []

    # 保存 JS 文件用于调试
    filename = f"downsub_js_{hash(js_url) % 10000}.js"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(js_content)
    logger.debug(f"💾 保存 JS 文件: {filename}")

    # 查找可能的 API 端点
    api_patterns_to_find = [
        # HTTP 请求相关
        r'(?:fetch|axios|XMLHttpRequest|\.get|\.post)\s*\(\s*[\'"`]([^\'"`]*(?:api|download|subtitle|sub)[^\'"`]*)[\'"`]',
        r'[\'"`]([^\'"`]*(?:/api/|/download/|/sub/)[^\'"`]*)[\'"`]',
        r'baseURL\s*:\s*[\'"`]([^\'"`]*)[\'"`]',
        r'endpoint\s*:\s*[\'"`]([^\'"`]*)[\'"`]',

        # YouTube 相关 API
        r'[\'"`]([^\'"`]*youtube[^\'"`]*api[^\'"`]*)[\'"`]',
        r'[\'"`]([^\'"`]*api[^\'"`]*youtube[^\'"`]*)[\'"`]',

        # 可能的内部 API
        r'[\'"`](/[^\'"`]*(?:process|parse|extract|fetch)[^\'"`]*)[\'"`]',
        r'[\'"`](https?://[^\'"`]*downsub[^\'"`]*)[\'"`]',

        # 表单提交相关
        r'action\s*:\s*[\'"`]([^\'"`]*)[\'"`]',
        r'url\s*:\s*[\'"`]([^\'"`]*)[\'"`]',

        # WebSocket 或其他通信
        r'[\'"`](wss?://[^\'"`]*)[\'"`]',
    ]

    for pattern in api_patterns_to_find:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        for match in matches:
            if match and len(match) > 3:  # 过滤太短的匹配
                patterns.append({
                    'url': match,
                    'source': js_url,
                    'pattern': pattern
                })

    # 查找 AJAX 请求模式
    ajax_patterns = [
        r'\.ajax\s*\(\s*{[^}]*url\s*:\s*[\'"`]([^\'"`]*)[\'"`]',
        r'fetch\s*\(\s*[\'"`]([^\'"`]*)[\'"`]',
        r'post\s*\(\s*[\'"`]([^\'"`]*)[\'"`]',
        r'get\s*\(\s*[\'"`]([^\'"`]*)[\'"`]',
    ]

    for pattern in ajax_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            patterns.append({
                'url': match,
                'source': js_url,
                'type': 'ajax',
                'pattern': pattern
            })

    # 查找可能的配置对象
    config_patterns = [
        r'(?:config|settings|options)\s*=\s*{([^}]*)API[^}]*}',
        r'API_BASE\s*:\s*[\'"`]([^\'"`]*)[\'"`]',
        r'API_URL\s*:\s*[\'"`]([^\'"`]*)[\'"`]',
    ]

    for pattern in config_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            patterns.append({
                'config': match,
                'source': js_url,
                'type': 'config'
            })

    logger.info(f"🔍 在 {js_url} 中找到 {len(patterns)} 个可能的 API 模式")

    return patterns


def test_api_endpoints(patterns):
    """测试发现的 API 端点"""

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://downsub.com/',
        'Origin': 'https://downsub.com'
    })

    test_video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'

    logger.info("🧪 测试发现的 API 端点...")

    unique_urls = set()
    for pattern in patterns:
        if 'url' in pattern:
            url = pattern['url']
            if url.startswith('/'):
                url = f"https://downsub.com{url}"
            unique_urls.add(url)

    working_endpoints = []

    for url in unique_urls:
        logger.info(f"🔗 测试端点: {url}")

        try:
            # 测试 GET 请求
            response = session.get(url, timeout=10)
            logger.info(f"  GET {response.status_code}: {url}")

            if response.status_code == 200:
                # 检查响应内容
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    logger.info(f"  ✅ JSON 响应: {len(response.text)} 字符")
                    working_endpoints.append({
                        'url': url,
                        'method': 'GET',
                        'content_type': content_type,
                        'content': response.text[:200]
                    })
                elif 'html' in content_type:
                    logger.info(f"  📄 HTML 响应: {len(response.text)} 字符")

            # 测试 POST 请求
            if 'api' in url.lower() or 'download' in url.lower():
                post_data = {
                    'url': test_video_url,
                    'video_url': test_video_url,
                    'link': test_video_url,
                    'videoUrl': test_video_url
                }

                response = session.post(url, data=post_data, timeout=10)
                logger.info(f"  POST {response.status_code}: {url}")

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        logger.info(f"  ✅ POST JSON 响应: {len(response.text)} 字符")
                        working_endpoints.append({
                            'url': url,
                            'method': 'POST',
                            'content_type': content_type,
                            'content': response.text[:200],
                            'data': post_data
                        })

        except Exception as e:
            logger.debug(f"  ❌ 端点失败: {e}")

        time.sleep(0.5)  # 避免请求过快

    return working_endpoints


def main():
    """主函数"""
    logger.info("🚀 开始逆向工程 DownSub.com API...")

    # 分析 JavaScript 文件
    patterns = analyze_downsub_js()

    if not patterns:
        logger.error("💥 无法找到任何 API 模式")
        return

    logger.info(f"📊 总共找到 {len(patterns)} 个 API 模式")

    # 保存发现的模式
    with open('downsub_api_patterns.json', 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    logger.info("💾 API 模式保存到 downsub_api_patterns.json")

    # 显示发现的模式
    for i, pattern in enumerate(patterns, 1):
        logger.info(f"  {i}. {pattern}")

    # 测试发现的端点
    working_endpoints = test_api_endpoints(patterns)

    if working_endpoints:
        logger.info(f"🎉 找到 {len(working_endpoints)} 个可能有效的端点:")
        for endpoint in working_endpoints:
            logger.info(f"  ✅ {endpoint['method']} {endpoint['url']}")
            logger.info(f"     Content-Type: {endpoint['content_type']}")
            logger.info(f"     Preview: {endpoint['content']}")

        # 保存有效端点
        with open('downsub_working_endpoints.json', 'w', encoding='utf-8') as f:
            json.dump(working_endpoints, f, indent=2, ensure_ascii=False)
        logger.info("💾 有效端点保存到 downsub_working_endpoints.json")
    else:
        logger.warning("⚠️  没有找到明显有效的端点")


if __name__ == '__main__':
    main()