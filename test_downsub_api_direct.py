#!/usr/bin/env python3
"""
直接测试 DownSub API 端点
"""

import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_downsub_api_endpoints():
    """直接测试 DownSub 的 API 端点"""

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://downsub.com/',
        'Origin': 'https://downsub.com',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    })

    test_video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'

    # 发现的 API 端点
    endpoints = [
        'https://get.downsub.com/',
        'https://get-info.downsub.com/',
    ]

    for endpoint in endpoints:
        logger.info(f"🔗 测试端点: {endpoint}")

        # 测试不同的 payload 格式
        payloads = [
            # JSON 格式
            {'url': test_video_url},
            {'video_url': test_video_url},
            {'link': test_video_url},
            {'videoUrl': test_video_url},

            # 可能的完整请求格式
            {
                'url': test_video_url,
                'type': 'youtube',
                'format': 'srt'
            },
            {
                'supported_sites': test_video_url,
                'submit': 'Download'
            }
        ]

        for i, payload in enumerate(payloads, 1):
            logger.info(f"  📦 测试 payload {i}: {payload}")

            try:
                # POST JSON
                response = session.post(endpoint, json=payload, timeout=30)
                logger.info(f"    JSON POST {response.status_code}: {len(response.text)} 字符")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"    ✅ JSON 响应: {json.dumps(data, indent=2)[:200]}...")

                        # 保存响应用于分析
                        with open(f'downsub_response_{i}.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)

                    except:
                        logger.info(f"    📄 文本响应: {response.text[:200]}...")

                # POST Form Data
                response = session.post(endpoint, data=payload, timeout=30)
                logger.info(f"    FORM POST {response.status_code}: {len(response.text)} 字符")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"    ✅ FORM JSON 响应: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        logger.info(f"    📄 FORM 文本响应: {response.text[:200]}...")

            except Exception as e:
                logger.warning(f"    ❌ 请求失败: {e}")

            time.sleep(1)  # 避免请求过快

        logger.info("")


def test_get_info_endpoint():
    """专门测试 get-info 端点，可能用于获取视频信息"""

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://downsub.com/',
        'Origin': 'https://downsub.com'
    })

    test_video_url = 'https://www.youtube.com/watch?v=zsTLDSibZnE'

    # 测试 GET 请求带参数
    params_list = [
        {'url': test_video_url},
        {'video': test_video_url},
        {'link': test_video_url},
        {'v': 'zsTLDSibZnE'},  # 只发送视频ID
    ]

    for params in params_list:
        logger.info(f"🔍 测试 GET 参数: {params}")

        try:
            response = session.get('https://get-info.downsub.com/', params=params, timeout=30)
            logger.info(f"  状态码: {response.status_code}")
            logger.info(f"  响应长度: {len(response.text)} 字符")

            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"  ✅ JSON: {json.dumps(data, indent=2)}")

                    # 如果有字幕信息，尝试下载
                    if 'subtitles' in data or 'subs' in data or 'tracks' in data:
                        logger.info("🎉 找到字幕信息！")
                        return data

                except:
                    logger.info(f"  📄 文本: {response.text}")

        except Exception as e:
            logger.warning(f"  ❌ 失败: {e}")

    return None


def test_with_video_id_only():
    """测试只使用视频ID"""

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://downsub.com/',
        'Origin': 'https://downsub.com'
    })

    video_id = 'zsTLDSibZnE'

    endpoints = [
        f'https://get.downsub.com/{video_id}',
        f'https://get-info.downsub.com/{video_id}',
        f'https://get.downsub.com/youtube/{video_id}',
        f'https://get-info.downsub.com/youtube/{video_id}',
    ]

    for endpoint in endpoints:
        logger.info(f"🎯 测试直接端点: {endpoint}")

        try:
            response = session.get(endpoint, timeout=30)
            logger.info(f"  GET {response.status_code}: {len(response.text)} 字符")

            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"  ✅ JSON: {json.dumps(data, indent=2)[:300]}...")

                    if 'subtitles' in data or 'subs' in data:
                        logger.info("🎉 找到字幕信息！")
                        return data

                except:
                    logger.info(f"  📄 文本: {response.text[:200]}...")

        except Exception as e:
            logger.warning(f"  ❌ 失败: {e}")

    return None


def main():
    """主函数"""
    logger.info("🚀 开始直接测试 DownSub API 端点...")

    # 测试 1: 基本 API 端点
    logger.info("\n1️⃣ 测试基本 API 端点...")
    test_downsub_api_endpoints()

    # 测试 2: get-info 端点
    logger.info("\n2️⃣ 测试 get-info 端点...")
    info_result = test_get_info_endpoint()

    # 测试 3: 直接使用视频ID
    logger.info("\n3️⃣ 测试直接视频ID端点...")
    id_result = test_with_video_id_only()

    # 总结
    logger.info("\n📊 测试总结:")
    if info_result or id_result:
        logger.info("🎉 成功找到有效的 API 调用方式！")
        if info_result:
            logger.info(f"  get-info 结果: {json.dumps(info_result, indent=2)}")
        if id_result:
            logger.info(f"  video-id 结果: {json.dumps(id_result, indent=2)}")
    else:
        logger.warning("⚠️  所有测试都没有返回字幕信息")
        logger.info("💡 建议检查网络连接或 DownSub.com 的当前状态")


if __name__ == '__main__':
    main()