#!/usr/bin/env python3
"""
解密 download.subtitle.to URL 参数中的加密数据
"""

import json
import base64
import urllib.parse
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_base64_padding(base64_string):
    """修复 base64 字符串的填充"""
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)
    return base64_string


def decrypt_url_parameter(encrypted_url_param):
    """尝试解密 URL 参数中的加密数据"""

    logger.info("🔐 开始解密 URL 参数...")

    try:
        # 修复 base64 填充
        fixed_param = fix_base64_padding(encrypted_url_param)
        logger.info(f"🔧 修复填充后: {len(fixed_param)} 字符")

        # Base64 解码
        decoded_bytes = base64.b64decode(fixed_param)
        decoded_text = decoded_bytes.decode('utf-8')
        logger.info(f"📄 Base64 解码成功: {len(decoded_text)} 字符")

        # 尝试解析为 JSON
        json_data = json.loads(decoded_text)
        logger.info("📊 JSON 解析成功:")

        for key, value in json_data.items():
            if isinstance(value, str) and len(value) > 50:
                logger.info(f"  {key}: {value[:50]}...")
            else:
                logger.info(f"  {key}: {value}")

        return json_data

    except Exception as e:
        logger.error(f"❌ 解密失败: {e}")
        return None


def try_aes_decryption(encrypted_data):
    """尝试 AES 解密（如果有加密数据的话）"""

    if not isinstance(encrypted_data, dict):
        return None

    if 'ct' not in encrypted_data or 'iv' not in encrypted_data:
        logger.info("📋 没有找到 AES 加密参数")
        return None

    logger.info("🔓 尝试 AES 解密...")

    try:
        # 这里需要安装 pycryptodome: pip install pycryptodome
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad

        # 提取加密参数
        ct = encrypted_data.get('ct', '')
        iv = encrypted_data.get('iv', '')
        salt = encrypted_data.get('s', '')

        logger.info(f"🔑 加密参数:")
        logger.info(f"  ct (密文): {ct[:50]}...")
        logger.info(f"  iv (初始向量): {iv}")
        logger.info(f"  s (盐值): {salt}")

        # 转换为字节
        ct_bytes = base64.b64decode(fix_base64_padding(ct))
        iv_bytes = bytes.fromhex(iv)

        logger.info(f"📐 数据长度:")
        logger.info(f"  密文: {len(ct_bytes)} 字节")
        logger.info(f"  IV: {len(iv_bytes)} 字节")

        # 需要密钥才能解密，这里先返回结构信息
        logger.info("🔐 需要找到解密密钥才能继续")
        return {
            'cipher_text': ct_bytes,
            'iv': iv_bytes,
            'salt': salt,
            'needs_key': True
        }

    except ImportError:
        logger.warning("⚠️ 需要安装 pycryptodome: pip install pycryptodome")
        return None
    except Exception as e:
        logger.error(f"❌ AES 解密失败: {e}")
        return None


def analyze_downsub_response():
    """分析 DownSub API 响应，看是否包含解密密钥信息"""

    logger.info("🔍 分析 DownSub API 响应...")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://downsub.com/',
        'Origin': 'https://downsub.com',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest'
    })

    # 使用我们知道有字幕的视频
    test_video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'
    payload = {'url': test_video_url}

    try:
        response = session.post('https://get.downsub.com/', json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            logger.info("📊 DownSub API 完整响应:")
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))

            # 查找可能的解密线索
            if result.get('urlSubtitle'):
                logger.info(f"🔗 发现字幕URL: {result['urlSubtitle']}")

            # 检查是否有其他可能包含密钥的字段
            for key, value in result.items():
                if isinstance(value, str) and ('key' in key.lower() or 'token' in key.lower() or 'secret' in key.lower()):
                    logger.info(f"🔑 可能的密钥字段: {key} = {value}")

            return result
        else:
            logger.error(f"❌ API 调用失败: {response.status_code}")

    except Exception as e:
        logger.error(f"💥 API 分析失败: {e}")

    return None


def main():
    """主函数"""
    logger.info("🚀 开始解密分析...")

    # 用户提供的加密 URL 参数
    encrypted_url_param = "eyJjdCI6IktXeXlVMnhkU2owMTdnZG9WZ1o1VFJxSFNrdkhVWG1yU3ZReTlFSi9CNS9yWmJZVkV3THJkMkVXdnVpUHJWYVR6Wlk0ZldSaVVyUkNabWdhWk5FMGl4WTlJYTVnQm5WbDdseWFUYTM4d1FybU1CMEl2Z0FpcTl6eURNVVYxVThkeE5Qem84V0hzVElEVE9aZ1ZCekl5N28rNkQ0YkE0K0ZQd0Rxam1kZjlkQkRER1Jzb0VPWkh5R25XUjYxZ3RrdnI4c09SanpuNzlIUGUxaE5xVFhJN1RUQm45Z1N3UlcyeVhra1JpRm1WODVJZ01VcDlLVk8veHlOZkdtVGNxbXFIc25iOVY3YktEL2ZSNTdlZFdWejdlQmlUbGRvVytnWHhJVitwU29GYTlkYndPNi9zRWpja1M4bTRpUXlSZVFVVTNndXl3R1JzTlV4TUIxUURoNGo2a0NwV05JSXFPeCtWNldRWTFZZDNEZ0ZMOTBnTDUzeG4vc2FXTk0veGtaTFFPUUQyRXZramE0MENNYldmdWFMTHE1eGpLMFVDZFEwaHVDMFBnQXloLzJwY1RtUWFhd0xXNlVxR3VNSGhNME8iLCJpdiI6IjJkOTc4MTNiNzE1ODU1ZWJhMTkzYzJhYTk3ZWFmYjI2IiwicyI6IjU2N2ZhYzViZWY2YzNjZjkifQ"

    # 步骤 1: 解密 URL 参数
    logger.info("\n1️⃣ 解密 URL 参数...")
    decrypted_data = decrypt_url_parameter(encrypted_url_param)

    # 步骤 2: 尝试 AES 解密
    if decrypted_data:
        logger.info("\n2️⃣ 尝试 AES 解密...")
        aes_result = try_aes_decryption(decrypted_data)

    # 步骤 3: 分析 DownSub API 响应
    logger.info("\n3️⃣ 分析 DownSub API...")
    api_result = analyze_downsub_response()

    # 总结
    logger.info("\n📊 解密分析总结:")

    if decrypted_data:
        logger.info("✅ 成功解析 URL 参数为 JSON")
        logger.info("🔐 确认使用 AES 加密 (ct, iv, s 参数)")

    if api_result:
        logger.info("✅ 成功获取 DownSub API 响应")

        # 重要发现：检查 urlSubtitle 字段
        if api_result.get('urlSubtitle'):
            subtitle_base_url = api_result['urlSubtitle']
            logger.info(f"🎯 关键发现: urlSubtitle = {subtitle_base_url}")
            logger.info("💡 这可能是字幕下载的基础URL")

    logger.info("\n🚀 下一步行动:")
    logger.info("1. 找到 DownSub.com 如何从 API 响应生成完整的下载链接")
    logger.info("2. 分析前端 JavaScript 中的加密/链接生成逻辑")
    logger.info("3. 实现完整的字幕获取流程")


if __name__ == '__main__':
    main()