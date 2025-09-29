#!/usr/bin/env python3
"""
分析用户提供的 download.subtitle.to 链接结构
"""

import json
import base64
import urllib.parse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_download_link():
    """分析用户提供的字幕下载链接"""

    # 用户提供的实际下载链接
    download_url = "https://download.subtitle.to/?title=%5BChinese%20Simplified%5D%20%E7%AB%8B%E5%85%9A%E8%87%AD%E9%AA%82YouTube%E7%BD%91%E5%8F%8B%EF%BC%9A%E4%B8%8D%E5%AD%A6%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%93%E4%B8%9A%EF%BC%8C%E6%9C%89%E4%BB%80%E4%B9%88%E8%84%B8%E5%90%83%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%E8%BF%99%E7%A2%97%E9%A5%AD%EF%BC%9F%E4%B8%BA%E4%BB%80%E4%B9%88%E7%8E%AF%E5%A2%83%2F%E6%9D%90%E6%96%99%2F%E6%9C%BA%E6%A2%B0%2F%E7%94%B5%E6%B0%94%2F%E8%83%BD%E5%8A%A8%E8%BF%99%E4%BA%9B%E4%BC%A0%E7%BB%9F%E5%B7%A5%E7%A7%91%EF%BC%8C%E9%9D%9E%E8%A6%81%E5%AD%A6%E7%BC%96%E7%A8%8B%E6%B7%B7%E8%BF%9B%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%EF%BC%9F%20%5BDownSub.com%5D&url=eyJjdCI6IktXeXlVMnhkU2owMTdnZG9WZ1o1VFJxSFNrdkhVWG1yU3ZReTlFSi9CNS9yWmJZVkV3THJkMkVXdnVpUHJWYVR6Wlk0ZldSaVVyUkNabWdhWk5FMGl4WTlJYTVnQm5WbDdseWFUYTM4d1FybU1CMEl2Z0FpcTl6eURNVVYxVThkeE5Qem84V0hzVElEVE9aZ1ZCekl5N28rNkQ0YkE0K0ZQd0Rxam1kZjlkQkRER1Jzb0VPWkh5R25XUjYxZ3RrdnI4c09SanpuNzlIUGUxaE5xVFhJN1RUQm45Z1N3UlcyeVhra1JpRm1MODVJZ01VcDlLVk8veHlOZkdtVGNxbXFIc25iOVY3YktEL2ZSNTdlZFdWejdlQmlUbGRvVytnWHhJVitwU29GYTlkYndPNi9zRWpja1M4bTRpUXlSZVFVVTNndXl3R1JzTlV4TUIxUURoNGo2a0NwV05JSXFPeCtWNldRWTFZZDNEZ0ZMOTBnTDUzeG4vc2FXTk0veGtaTFFPUUQyRXZramE0MENNYldmdWFMTHE1eGpLMFVDZFEwaHVDMFBnQXloLzJwY1RtUWFhd0xXNlVxR3VNSGhNME8iLCJpdiI6IjJkOTc4MTNiNzE1ODU1ZWJhMTkzYzJhYTk3ZWFmYjI2IiwicyI6IjU2N2ZhYzViZWY2YzNjZjkifQ&type=txt"

    logger.info("🔍 分析下载链接结构...")

    # 解析 URL 参数
    parsed_url = urllib.parse.urlparse(download_url)
    params = urllib.parse.parse_qs(parsed_url.query)

    logger.info(f"📋 URL 组件:")
    logger.info(f"  域名: {parsed_url.netloc}")
    logger.info(f"  路径: {parsed_url.path}")

    # 分析各个参数
    for key, value in params.items():
        logger.info(f"  {key}: {value[0][:100]}{'...' if len(value[0]) > 100 else ''}")

    # 解码 title 参数
    if 'title' in params:
        title_encoded = params['title'][0]
        title_decoded = urllib.parse.unquote(title_encoded)
        logger.info(f"📝 解码后的标题: {title_decoded}")

    # 分析 URL 参数中的加密数据
    if 'url' in params:
        encrypted_data = params['url'][0]
        logger.info(f"🔐 加密数据长度: {len(encrypted_data)} 字符")

        try:
            # 尝试 base64 解码
            decoded_bytes = base64.b64decode(encrypted_data)
            decoded_text = decoded_bytes.decode('utf-8')
            logger.info(f"📄 Base64 解码成功:")

            # 尝试解析为 JSON
            try:
                json_data = json.loads(decoded_text)
                logger.info(f"📊 JSON 数据结构:")
                for key, value in json_data.items():
                    if isinstance(value, str) and len(value) > 50:
                        logger.info(f"  {key}: {value[:50]}...")
                    else:
                        logger.info(f"  {key}: {value}")

                return json_data

            except json.JSONDecodeError:
                logger.info(f"📄 非 JSON 格式: {decoded_text[:200]}...")
                return decoded_text

        except Exception as e:
            logger.warning(f"❌ Base64 解码失败: {e}")

            # 尝试 URL 解码
            try:
                url_decoded = urllib.parse.unquote(encrypted_data)
                logger.info(f"🔗 URL 解码: {url_decoded[:200]}...")
                return url_decoded
            except Exception as e2:
                logger.error(f"❌ URL 解码也失败: {e2}")

    # 分析 type 参数
    if 'type' in params:
        file_type = params['type'][0]
        logger.info(f"📁 文件类型: {file_type}")

    return None


def try_download_subtitle():
    """尝试下载字幕内容"""

    download_url = "https://download.subtitle.to/?title=%5BChinese%20Simplified%5D%20%E7%AB%8B%E5%85%9A%E8%87%AD%E9%AA%82YouTube%E7%BD%91%E5%8F%8B%EF%BC%9A%E4%B8%8D%E5%AD%A6%E8%AE%A1%E7%AE%97%E6%9C%BA%E4%B8%93%E4%B8%9A%EF%BC%8C%E6%9C%89%E4%BB%80%E4%B9%88%E8%84%B8%E5%90%83%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%E8%BF%99%E7%A2%97%E9%A5%AD%EF%BC%9F%E4%B8%BA%E4%BB%80%E4%B9%88%E7%8E%AF%E5%A2%83%2F%E6%9D%90%E6%96%99%2F%E6%9C%BA%E6%A2%B0%2F%E7%94%B5%E6%B0%94%2F%E8%83%BD%E5%8A%A8%E8%BF%99%E4%BA%9B%E4%BC%A0%E7%BB%9F%E5%B7%A5%E7%A7%91%EF%BC%8C%E9%9D%9E%E8%A6%81%E5%AD%A6%E7%BC%96%E7%A8%8B%E6%B7%B7%E8%BF%9B%E7%A7%91%E6%8A%80%E4%BA%92%E8%81%94%E7%BD%91%EF%BC%9F%20%5BDownSub.com%5D&url=eyJjdCI6IktXeXlVMnhkU2owMTdnZG9WZ1o1VFJxSFNrdkhVWG1yU3ZReTlFSi9CNS9yWmJZVkV3THJkMkVXdnVpUHJWYVR6Wlk0ZldSaVVyUkNabWdhWk5FMGl4WTlJYTVnQm5WbDdseWFUYTM4d1FybU1CMEl2Z0FpcTl6eURNVVYxVThkeE5Qem84V0hzVElEVE9aZ1ZCekl5N28rNkQ0YkE0K0ZQd0Rxam1kZjlkQkRER1Jzb0VPWkh5R25XUjYxZ3RrdnI4c09SanpuNzlIUGUxaE5xVFhJN1RUQm45Z1N3UlcyeVhra1JpRm1MODVJZ01VcDlLVk8veHlOZkdtVGNxbXFIc25iOVY3YktEL2ZSNTdlZFdWejdlQmlUbGRvVytnWHhJVitwU29GYTlkYndPNi9zRWpja1M4bTRpUXlSZVFVVTNndXl3R1JzTlV4TUIxUURoNGo2a0NwV05JSXFPeCtWNldRWTFZZDNEZ0ZMOTBnTDUzeG4vc2FXTk0veGtaTFFPUUQyRXZramE0MENNYldmdWFMTHE1eGpLMFVDZFEwaHVDMFBnQXloLzJwY1RtUWFhd0xXNlVxR3VNSGhNME8iLCJpdiI6IjJkOTc4MTNiNzE1ODU1ZWJhMTkzYzJhYTk3ZWFmYjI2IiwicyI6IjU2N2ZhYzViZWY2YzNjZjkifQ&type=txt"

    logger.info("📥 尝试下载字幕内容...")

    import requests

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Referer': 'https://downsub.com/',
    })

    try:
        response = session.get(download_url, timeout=30)
        logger.info(f"📊 下载响应:")
        logger.info(f"  状态码: {response.status_code}")
        logger.info(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
        logger.info(f"  内容长度: {len(response.text)} 字符")

        if response.status_code == 200:
            content = response.text

            # 保存字幕内容
            with open('downloaded_subtitle.txt', 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"📄 字幕内容预览:")
            logger.info(content[:500] + ('...' if len(content) > 500 else ''))

            return content
        else:
            logger.error(f"❌ 下载失败: {response.status_code}")
            logger.error(f"响应内容: {response.text[:200]}")

    except Exception as e:
        logger.error(f"💥 下载异常: {e}")

    return None


def main():
    """主函数"""
    logger.info("🚀 开始分析 download.subtitle.to 链接...")

    # 分析链接结构
    logger.info("\n1️⃣ 分析链接结构...")
    encrypted_data = analyze_download_link()

    # 尝试下载内容
    logger.info("\n2️⃣ 尝试下载字幕...")
    subtitle_content = try_download_subtitle()

    # 总结
    logger.info("\n📊 分析总结:")
    if encrypted_data:
        logger.info("✅ 成功解析加密数据结构")
        if isinstance(encrypted_data, dict):
            logger.info(f"🔐 发现加密参数: ct, iv, s")
            logger.info("💡 这表明使用了对称加密（可能是 AES）")

    if subtitle_content:
        logger.info("✅ 成功下载字幕内容")
        logger.info("💾 字幕已保存到 downloaded_subtitle.txt")
    else:
        logger.warning("⚠️ 字幕下载失败")

    logger.info("\n🎯 下一步计划:")
    logger.info("1. 分析加密算法（AES 解密）")
    logger.info("2. 找到 DownSub.com 如何生成这些链接")
    logger.info("3. 集成到现有的 DownSub fetcher 中")


if __name__ == '__main__':
    main()