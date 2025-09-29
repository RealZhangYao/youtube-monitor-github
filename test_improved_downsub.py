#!/usr/bin/env python3
"""
测试改进后的 DownSub fetcher 实现
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


def test_improved_downsub():
    """测试改进后的 DownSub fetcher"""

    logger.info("🚀 测试改进后的 DownSub fetcher...")

    # 初始化 fetcher
    fetcher = DownSubFetcher()

    # 使用用户确认有字幕的视频ID
    test_video_id = 'zsTLDSibZnE'

    logger.info(f"📺 测试视频 ID: {test_video_id}")
    logger.info(f"🔗 YouTube URL: https://www.youtube.com/watch?v={test_video_id}")

    # 尝试获取字幕
    logger.info("\n📋 开始多策略字幕获取...")

    transcript, language = fetcher.fetch_transcript(test_video_id)

    # 结果分析
    if transcript:
        logger.info("🎉 成功获取字幕！")
        logger.info(f"📝 语言: {language}")
        logger.info(f"📏 字幕长度: {len(transcript)} 字符")
        logger.info(f"📄 内容预览:")

        # 显示前500字符
        preview = transcript[:500]
        logger.info(f"{preview}...")

        # 保存完整字幕
        filename = f'transcript_improved_{test_video_id}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(transcript)
        logger.info(f"💾 完整字幕保存到: {filename}")

        # 分析字幕质量
        analyze_subtitle_quality(transcript)

        return True

    else:
        logger.error("❌ 字幕获取失败")
        logger.info("💡 可能的原因:")
        logger.info("  1. 该视频确实没有字幕")
        logger.info("  2. DownSub.com 服务器暂时不可用")
        logger.info("  3. 需要进一步改进逆向工程方法")

        return False


def analyze_subtitle_quality(transcript):
    """分析字幕质量"""
    logger.info("\n📊 字幕质量分析:")

    # 基本统计
    char_count = len(transcript)
    line_count = len(transcript.split('\n'))
    word_count = len(transcript.split())

    logger.info(f"  📏 总字符数: {char_count:,}")
    logger.info(f"  📝 总行数: {line_count:,}")
    logger.info(f"  📖 总词数: {word_count:,}")

    # 语言检测
    chinese_chars = sum(1 for char in transcript if ord(char) > 127)
    chinese_ratio = chinese_chars / char_count if char_count > 0 else 0

    if chinese_ratio > 0.3:
        logger.info(f"  🇨🇳 中文字符比例: {chinese_ratio:.1%} (中文字幕)")
    else:
        logger.info(f"  🇺🇸 中文字符比例: {chinese_ratio:.1%} (英文字幕)")

    # 内容质量
    if char_count > 1000:
        logger.info("  ✅ 字幕长度充足，内容丰富")
    elif char_count > 500:
        logger.info("  ⚠️ 字幕长度中等")
    else:
        logger.info("  ❌ 字幕长度较短，可能不完整")

    # 格式检测
    if '\n' in transcript and line_count > 10:
        logger.info("  ✅ 字幕格式良好，有适当的分行")
    else:
        logger.info("  ⚠️ 字幕可能需要格式优化")


def test_multiple_strategies():
    """测试不同的字幕获取策略"""
    logger.info("\n🧪 测试多种字幕获取策略...")

    fetcher = DownSubFetcher()
    test_videos = [
        ('zsTLDSibZnE', '用户确认有字幕的视频'),
        ('dQw4w9WgXcQ', '经典热门视频'),
        ('jNQXAC9IVRw', '另一个热门视频'),
    ]

    results = []

    for video_id, description in test_videos:
        logger.info(f"\n🎯 测试: {description} ({video_id})")

        try:
            transcript, language = fetcher.fetch_transcript(video_id)

            result = {
                'video_id': video_id,
                'description': description,
                'success': transcript is not None,
                'language': language,
                'length': len(transcript) if transcript else 0
            }

            results.append(result)

            if transcript:
                logger.info(f"✅ 成功: {len(transcript)} 字符, 语言: {language}")

                # 保存字幕用于比较
                with open(f'transcript_test_{video_id}.txt', 'w', encoding='utf-8') as f:
                    f.write(transcript)

            else:
                logger.info("❌ 失败")

        except Exception as e:
            logger.error(f"💥 异常: {e}")
            results.append({
                'video_id': video_id,
                'description': description,
                'success': False,
                'language': None,
                'length': 0,
                'error': str(e)
            })

    # 总结报告
    logger.info("\n📊 测试总结报告:")
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)

    logger.info(f"成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    for result in results:
        status = "✅" if result['success'] else "❌"
        logger.info(f"{status} {result['video_id']}: {result['description']}")
        if result['success']:
            logger.info(f"    语言: {result['language']}, 长度: {result['length']} 字符")
        elif 'error' in result:
            logger.info(f"    错误: {result['error']}")

    return results


def main():
    """主测试函数"""
    logger.info("🎯 开始测试改进后的 DownSub 逆向工程实现...")

    # 测试 1: 重点测试用户确认有字幕的视频
    logger.info("\n1️⃣ 重点测试目标视频...")
    success = test_improved_downsub()

    if success:
        # 测试 2: 测试多个视频以验证通用性
        logger.info("\n2️⃣ 测试多个视频验证通用性...")
        test_multiple_strategies()

        logger.info("\n🎉 测试完成！DownSub 逆向工程实现有效！")
    else:
        logger.warning("\n⚠️ 主要目标视频测试失败")
        logger.info("💡 建议:")
        logger.info("1. 检查网络连接")
        logger.info("2. 验证 DownSub.com 服务状态")
        logger.info("3. 考虑进一步改进逆向工程方法")

    logger.info("\n📁 生成的文件:")
    logger.info("- transcript_improved_*.txt: 改进后获取的字幕")
    logger.info("- transcript_test_*.txt: 测试获取的字幕")


if __name__ == '__main__':
    main()