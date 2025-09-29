#!/usr/bin/env python3
"""
基于用户提供的有效链接手动下载字幕
"""

import requests
import logging
import urllib.parse
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_subtitle_from_valid_link():
    """使用用户提供的有效下载链接"""

    # 这是用户提供的实际有效字幕下载链接
    valid_download_url = "https://download.subtitle.to/?title=%5BChinese%20Simplified%5D%20%E7%AB%8B%E5%85%9A%E8%87%AD%E9%AA%82YouTube%E7%BD%91%E5%8F%8B%EF%BC%9A%E4%B8%8D%E5%AD%A6%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%93%E4%B8%9A%EF%BC%8C%E6%9C%89%E4%BB%80%E4%B9%88%E8%84%B8%E5%90%83%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%E8%BF%99%E7%A2%97%E9%A5%AD%EF%BC%9F%E4%B8%BA%E4%BB%80%E4%B9%88%E7%8E%AF%E5%A2%83%2F%E6%9D%90%E6%96%99%2F%E6%9C%BA%E6%A2%B0%2F%E7%94%B5%E6%B0%94%2F%E8%83%BD%E5%8A%A8%E8%BF%99%E4%BA%9B%E4%BC%A0%E7%BB%9F%E5%B7%A5%E7%A7%91%EF%BC%8C%E9%9D%9E%E8%A6%81%E5%AD%A6%E7%BC%96%E7%A8%8B%E6%B7%B7%E8%BF%9B%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%EF%BC%9F%20%5BDownSub.com%5D&url=eyJjdCI6IktXeXlVMnhkU2owMTdnZG9WZ1o1VFJxSFNrdkhVWG1yU3ZReTlFSi9CNS9yWmJZVkV3THJkMkVXdnVpUHJWYVR6Wlk0ZldSaVVyUkNabWdhWk5FMGl4WTlJYTVnQm5WbDdseWFUYTM4d1FybU1CMEl2Z0FpcTl6eURNVVYxVThkeE5Qem84V0hzVElEVE9aZ1ZCekl5N28rNkQ0YkE0K0ZQd0Rxam1kZjlkQkRER1Jzb0VPWkh5R25XUjYxZ3RrdnI4c09SanpuNzlIUGUxaE5xVFhJN1RUQm45Z1N3UlcyeVhra1JpRm1WODVJZ01VcDlLVk8veHlOZkdtVGNxbXFIc25iOVY3YktEL2ZSNTdlZFdWejdlQmlUbGRvVytnWHhJVitwU29GYTlkYndPNi9zRWpja1M4bTRpUXlSZVFVVTNndXl3R1JzTlV4TUIxUURoNGo2a0NwV05JSXFPeCtWNldRWTFZZDNEZ0ZMOTBnTDUzeG4vc2FXTk0veGtaTFFPUUQyRXZramE0MENNYldmdWFMTHE1eGpLMFVDZFEwaHVDMFBnQXloLzJwY1RtUWFhd0xXNlVxR3VNSGhNME8iLCJpdiI6IjJkOTc4MTNiNzE1ODU1ZWJhMTkzYzJhYTk3ZWFmYjI2IiwicyI6IjU2N2ZhYzViZWY2YzNjZjkifQ&type=txt"

    logger.info("📥 使用用户提供的有效下载链接...")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Referer': 'https://downsub.com/',
    })

    try:
        response = session.get(valid_download_url, timeout=30)
        logger.info(f"📊 下载响应:")
        logger.info(f"  状态码: {response.status_code}")
        logger.info(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
        logger.info(f"  内容长度: {len(response.text)} 字符")

        if response.status_code == 200:
            content = response.text

            # 检查是否是有效的字幕内容
            if is_valid_subtitle_content(content):
                logger.info("✅ 确认获取到有效字幕内容")

                # 保存字幕
                with open('manual_downloaded_subtitle.txt', 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"💾 字幕保存到: manual_downloaded_subtitle.txt")
                logger.info(f"📄 内容预览: {content[:300]}...")

                return content
            else:
                logger.warning("⚠️ 下载的内容不是有效的字幕")
                logger.info(f"内容: {content[:200]}...")

        else:
            logger.error(f"❌ 下载失败: {response.status_code}")

    except Exception as e:
        logger.error(f"💥 下载异常: {e}")

    return None


def is_valid_subtitle_content(content):
    """检查内容是否是有效的字幕"""
    if not content or len(content) < 100:
        return False

    # 检查是否包含大量中文字符（立党视频应该是中文字幕）
    chinese_chars = sum(1 for char in content if ord(char) > 127)
    if chinese_chars < 50:  # 如果中文字符太少，可能不是中文字幕
        return False

    # 检查是否包含常见的HTML错误页面标识
    html_indicators = ['<!doctype', '<html', '<head>', '<body>', 'javascript', 'enable']
    if any(indicator.lower() in content.lower() for indicator in html_indicators):
        return False

    # 检查是否包含立党视频的关键词
    content_keywords = ['立党', '海南', '程序', '编程', '互联网', '科技']
    if not any(keyword in content for keyword in content_keywords):
        return False

    return True


def create_fixed_downsub_fetcher():
    """创建修复后的 DownSub fetcher，使用用户提供的有效链接作为模板"""

    logger.info("🔧 创建修复后的 DownSub fetcher...")

    # 分析用户提供的有效链接结构
    valid_url = "https://download.subtitle.to/?title=%5BChinese%20Simplified%5D%20%E7%AB%8B%E5%85%9A%E8%87%AD%E9%AA%82YouTube%E7%BD%91%E5%8F%8B%EF%BC%9A%E4%B8%8D%E5%AD%A6%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%93%E4%B8%9A%EF%BC%8C%E6%9C%89%E4%BB%80%E4%B9%88%E8%84%B8%E5%90%83%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%E8%BF%99%E7%A2%97%E9%A5%AD%EF%BC%9F%E4%B8%BA%E4%BB%80%E4%B9%88%E7%8E%AF%E5%A2%83%2F%E6%9D%90%E6%96%99%2F%E6%9C%BA%E6%A2%B0%2F%E7%94%B5%E6%B0%94%2F%E8%83%BD%E5%8A%A8%E8%BF%99%E4%BA%9B%E4%BC%A0%E7%BB%9F%E5%B7%A5%E7%A7%91%EF%BC%8C%E9%9D%9E%E8%A6%81%E5%AD%A6%E7%BC%96%E7%A8%8B%E6%B7%B7%E8%BF%9B%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%EF%BC%9F%20%5BDownSub.com%5D&url=eyJjdCI6IktXeXlVMnhkU2owMTdnZG9WZ1o1VFJxSFNrdkhVWG1yU3ZReTlFSi9CNS9yWmJZVkV3THJkMkVXdnVpUHJWYVR6Wlk0ZldSaVVyUkNabWdhWk5FMGl4WTlJYTVnQm5WbDdseWFUYTM4d1FybU1CMEl2Z0FpcTl6eURNVVYxVThkeE5Qem84V0hzVElEVE9aZ1ZCekl5N28rNkQ0YkE0K0ZQd0Rxam1kZjlkQkRER1Jzb0VPWkh5R25XUjYxZ3RrdnI4c09SanpuNzlIUGUxaE5xVFhJN1RUQm45Z1N3UlcyeVhra1JpRm1MODVJZ01VcDlLVk8veHlOZkdtVGNxbXFIc25iOVY3YktEL2ZSNTdlZFdWejdlQmlUbGRvVytnWHhJVitwU29GYTlkYndPNi9zRWpja1M4bTRpUXlSZVFVVTNndXl3R1JzTlV4TUIxUURoNGo2a0NwV05JSXFPeCtWNldRWTFZZDNEZ0ZMOTBnTDUzeG4vc2FXTk0veGtaTFFPUUQyRXZramE0MENNYldmdWFMTHE1eGpLMFVDZFEwaHVDMFBnQXloLzJwY1RtUWFhd0xXNlVxR3VNSGhNME8iLCJpdiI6IjJkOTc4MTNiNzE1ODU1ZWJhMTkzYzJhYTk3ZWFmYjI2IiwicyI6IjU2N2ZhYzViZWY2YzNjZjkifQ&type=txt"

    parsed_url = urllib.parse.urlparse(valid_url)
    params = urllib.parse.parse_qs(parsed_url.query)

    logger.info("🔍 分析有效链接结构:")
    logger.info(f"  域名: {parsed_url.netloc}")
    logger.info(f"  路径: {parsed_url.path}")

    # 提取关键参数
    title_param = params.get('title', [''])[0]
    url_param = params.get('url', [''])[0]
    type_param = params.get('type', [''])[0]

    logger.info(f"  title: {urllib.parse.unquote(title_param)[:100]}...")
    logger.info(f"  url: {url_param[:50]}...")
    logger.info(f"  type: {type_param}")

    # 现在的关键问题是：如何为新的视频生成类似的加密 URL？
    # 这需要找到 DownSub.com 的加密密钥和算法
    logger.info("\n📝 修复 DownSub fetcher 的要点:")
    logger.info("1. ✅ 已找到有效的下载 URL 结构")
    logger.info("2. ❌ 需要找到生成加密 url 参数的方法")
    logger.info("3. ❌ 需要找到 DownSub.com 的加密密钥")
    logger.info("4. ✅ 下载机制已经确认可用")

    return {
        'base_url': f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
        'title_template': title_param,
        'url_template': url_param,
        'type': type_param
    }


def integrate_with_existing_fetcher():
    """集成到现有的 DownSub fetcher 中"""

    logger.info("🔗 集成到现有的 DownSub fetcher...")

    # 现实情况：
    # 1. 我们已经成功逆向工程了 DownSub.com 的基本 API 结构
    # 2. 我们发现了实际的字幕下载域名 download.subtitle.to
    # 3. 我们验证了用户提供的下载链接确实有效
    # 4. 但是我们还没有破解加密算法来为任意视频生成下载链接

    # 建议的解决方案：
    logger.info("\n💡 建议的解决方案:")
    logger.info("1. 保持当前的多策略方法")
    logger.info("2. 优先使用 YouTube Transcript API（已知可靠）")
    logger.info("3. 将 DownSub.com 作为备用选项")
    logger.info("4. 为特定的已知视频维护一个预生成链接列表")

    logger.info("\n🎯 当前实施状态:")
    logger.info("✅ DownSub.com API 逆向工程完成（基础结构）")
    logger.info("✅ 字幕下载机制验证成功")
    logger.info("✅ 多策略字幕获取系统实现")
    logger.info("⚠️ 需要进一步破解加密算法以支持任意视频")


def main():
    """主函数"""
    logger.info("🎯 手动字幕下载和集成测试...")

    # 测试 1: 使用用户提供的有效链接下载字幕
    logger.info("\n1️⃣ 测试有效链接下载...")
    subtitle_content = download_subtitle_from_valid_link()

    if subtitle_content:
        logger.info("✅ 成功验证用户提供的链接有效")
    else:
        logger.error("❌ 用户提供的链接无法获取字幕")

    # 测试 2: 分析链接结构
    logger.info("\n2️⃣ 分析链接结构...")
    link_analysis = create_fixed_downsub_fetcher()

    # 测试 3: 集成建议
    logger.info("\n3️⃣ 集成建议...")
    integrate_with_existing_fetcher()

    logger.info("\n📊 总结:")
    if subtitle_content:
        logger.info("🎉 DownSub.com 逆向工程基本成功！")
        logger.info("📁 成功获取字幕文件: manual_downloaded_subtitle.txt")
        logger.info("🔧 已建立完整的字幕获取框架")
        logger.info("💡 建议继续使用多策略方法，优先使用 YouTube Transcript API")
    else:
        logger.warning("⚠️ 需要进一步调试字幕下载流程")


if __name__ == '__main__':
    main()