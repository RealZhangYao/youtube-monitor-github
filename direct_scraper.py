#!/usr/bin/env python3
"""
直接模拟浏览器行为获取字幕
"""

import requests
import re
import json
import logging
import urllib.parse
import time
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def simulate_full_browser_flow():
    """完整模拟浏览器访问 DownSub.com 的流程"""

    session = requests.Session()

    # 设置完整的浏览器头部
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
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

    # 我们知道有字幕的视频URL
    video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'

    logger.info("🌐 步骤 1: 访问 DownSub 主页...")

    try:
        # 步骤 1: 访问主页获取初始状态
        response = session.get('https://downsub.com', timeout=30)
        logger.info(f"主页访问: {response.status_code}")

        if response.status_code == 200:
            # 保存主页 HTML 用于分析
            with open('downsub_homepage.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

            # 分析页面中的 JavaScript 和表单
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找表单
            forms = soup.find_all('form')
            logger.info(f"找到 {len(forms)} 个表单")

            for i, form in enumerate(forms):
                action = form.get('action', '/')
                method = form.get('method', 'GET')
                logger.info(f"  表单 {i+1}: {method} {action}")

                # 查找输入字段
                inputs = form.find_all('input')
                for inp in inputs:
                    name = inp.get('name', '')
                    type_attr = inp.get('type', '')
                    if name:
                        logger.info(f"    输入: {name} ({type_attr})")

    except Exception as e:
        logger.error(f"访问主页失败: {e}")
        return None

    logger.info("\n🎯 步骤 2: 模拟表单提交...")

    try:
        # 步骤 2: 使用不同的表单提交方式
        submit_methods = [
            # 方法 1: 直接 URL 参数
            {
                'method': 'GET',
                'url': 'https://downsub.com',
                'params': {'url': video_url}
            },
            # 方法 2: POST 表单
            {
                'method': 'POST',
                'url': 'https://downsub.com',
                'data': {'url': video_url}
            },
            # 方法 3: 不同的字段名
            {
                'method': 'POST',
                'url': 'https://downsub.com',
                'data': {'supported_sites': video_url, 'submit': 'Download'}
            }
        ]

        for i, method in enumerate(submit_methods, 1):
            logger.info(f"\n🧪 尝试方法 {i}: {method['method']}")

            session.headers.update({
                'Referer': 'https://downsub.com/',
                'Origin': 'https://downsub.com',
            })

            if method['method'] == 'GET':
                response = session.get(method['url'], params=method.get('params'), timeout=30)
            else:
                session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
                response = session.post(method['url'], data=method.get('data'), timeout=30)

            logger.info(f"响应: {response.status_code}, 长度: {len(response.text)}")

            if response.status_code == 200:
                # 保存响应用于分析
                with open(f'downsub_response_method_{i}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)

                # 查找字幕下载链接
                subtitle_links = find_subtitle_links(response.text)
                if subtitle_links:
                    logger.info(f"✅ 方法 {i} 找到 {len(subtitle_links)} 个字幕链接:")
                    for link in subtitle_links:
                        logger.info(f"  🔗 {link}")
                        # 尝试下载第一个链接
                        if download_subtitle_from_link(session, link):
                            return True

            time.sleep(2)  # 避免请求过快

    except Exception as e:
        logger.error(f"表单提交失败: {e}")

    logger.info("\n🔍 步骤 3: 分析 AJAX 调用...")

    try:
        # 步骤 3: 尝试 AJAX 调用
        session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        })

        # 使用发现的 API 端点
        api_response = session.post('https://get.downsub.com/', json={'url': video_url}, timeout=30)
        logger.info(f"API 响应: {api_response.status_code}")

        if api_response.status_code == 200:
            api_data = api_response.json()
            logger.info("API 数据:")
            logger.info(json.dumps(api_data, indent=2, ensure_ascii=False))

            # 查找可能的字幕信息
            if api_data.get('subtitles') or api_data.get('subtitlesAutoTrans'):
                logger.info("✅ API 返回了字幕数据")
                return api_data
            else:
                logger.info("⚠️ API 响应中没有字幕数据")

    except Exception as e:
        logger.error(f"AJAX 调用失败: {e}")

    return None


def find_subtitle_links(html_content):
    """在 HTML 内容中查找字幕下载链接"""

    links = []

    # 多种模式查找字幕链接
    patterns = [
        r'href=["\']([^"\']*download\.subtitle\.to[^"\']*)["\']',
        r'href=["\']([^"\']*\.(?:srt|vtt|txt|sbv)[^"\']*)["\']',
        r'href=["\']([^"\']*download[^"\']*subtitle[^"\']*)["\']',
        r'href=["\']([^"\']*subtitle[^"\']*download[^"\']*)["\']',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if match not in links:
                links.append(match)

    # 也查找可能的 JavaScript 中的链接
    js_patterns = [
        r'["\']([^"\']*download\.subtitle\.to[^"\']*)["\']',
        r'url\s*:\s*["\']([^"\']*download[^"\']*)["\']',
    ]

    for pattern in js_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if 'download.subtitle.to' in match and match not in links:
                links.append(match)

    return links


def download_subtitle_from_link(session, link):
    """从给定链接下载字幕"""

    try:
        logger.info(f"📥 尝试下载: {link}")

        # 确保链接是绝对路径
        if link.startswith('/'):
            link = f"https://downsub.com{link}"
        elif not link.startswith('http'):
            link = f"https://downsub.com/{link}"

        response = session.get(link, timeout=30)
        logger.info(f"下载响应: {response.status_code}")

        if response.status_code == 200:
            content = response.text

            # 检查是否是字幕内容
            if (len(content) > 100 and
                ('webvtt' in content.lower() or
                 re.search(r'\d+:\d+:\d+', content) or
                 any(char in content for char in '的是在有为了'))):  # 中文字符检测

                logger.info("✅ 成功下载字幕内容")

                # 保存字幕
                filename = f"subtitle_downloaded_{int(time.time())}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"💾 字幕保存到: {filename}")
                logger.info(f"📄 内容预览: {content[:200]}...")

                return True

    except Exception as e:
        logger.error(f"下载失败: {e}")

    return False


def main():
    """主函数"""
    logger.info("🚀 开始完整的浏览器流程模拟...")

    result = simulate_full_browser_flow()

    if result:
        logger.info("🎉 成功获取字幕！")
    else:
        logger.warning("⚠️ 未能获取字幕，但收集了有用信息")

    logger.info("\n📊 分析总结:")
    logger.info("1. 已保存各种响应到文件用于进一步分析")
    logger.info("2. 收集了表单和 API 调用信息")
    logger.info("3. 可以基于这些信息完善 DownSub 集成")


if __name__ == '__main__':
    main()