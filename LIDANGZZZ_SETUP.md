# @lidangzzz 频道监控设置指南

本项目已经被专门配置用于监控 @lidangzzz 频道，并使用 downsub.com 作为首选的字幕下载方式。

## 🎯 新功能

### 1. 专门针对 @lidangzzz 频道
- 自动通过用户名查找频道ID
- 无需手动查找和配置频道ID
- 支持 YouTube 新的用户名格式

### 2. DownSub.com 字幕下载
- 使用 downsub.com 作为首选字幕下载方式
- 更高的成功率和稳定性
- 支持多种字幕格式 (SRT, VTT)
- 自动选择最佳语言字幕

### 3. 增强的配置选项
- `TARGET_USERNAME`: 目标用户名 (默认: lidangzzz)
- `USE_DOWNSUB`: 是否使用 DownSub.com (默认: true)
- `GET_LATEST`: 总是获取最新视频，忽略处理状态 (默认: false)

## 🚀 快速设置

### 1. GitHub Secrets 配置

在你的 GitHub 仓库中设置以下 Secrets:

| Secret 名称 | 说明 | 必填 |
|------------|------|------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 密钥 | ✅ |
| `GEMINI_API_KEY` | Google AI Studio API 密钥 | ✅ |
| `GMAIL_USER` | Gmail 邮箱地址 | ✅ |
| `GMAIL_APP_PASSWORD` | Gmail 应用专用密码 | ✅ |
| `RECIPIENT_EMAIL` | 接收通知的邮箱 | ✅ |
| `TARGET_USERNAME` | 目标用户名 | ❌ (默认: lidangzzz) |
| `USE_DOWNSUB` | 使用 DownSub.com | ❌ (默认: true) |
| `GET_LATEST` | 总是获取最新视频 | ❌ (默认: false) |

### 2. 触发监控

#### 自动触发
- 项目默认每12小时自动运行一次
- 检测 @lidangzzz 频道的最新视频

#### 手动触发
1. 进入 GitHub Actions
2. 选择 "YouTube Monitor" 工作流
3. 点击 "Run workflow"
4. 选择选项：
   - **测试模式**: 验证所有连接和API
   - **获取最新视频**: 总是处理最新视频（忽略之前是否已处理）

## 🔧 本地测试

### 1. 环境设置

```bash
# 克隆仓库
git clone <your-fork-url>
cd youtube-monitor-github

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export YOUTUBE_API_KEY="your-api-key"
export TARGET_USERNAME="lidangzzz"
export USE_DOWNSUB="true"
export GET_LATEST="true"  # 总是获取最新视频
```

### 2. 运行测试

```bash
# 测试所有功能
python test_lidangzzz.py

# 测试模式运行
export TEST_MODE="true"
python src/main.py
```

## 📧 邮件通知格式

你将收到包含以下信息的邮件：

- 📺 **视频标题和链接**
- 📝 **AI 生成的内容摘要**
- 🕒 **发布时间**
- 📊 **观看次数和时长**
- 🎯 **从 downsub.com 提取的高质量字幕**

## 🎯 GET_LATEST 模式使用场景

### 什么时候使用 GET_LATEST=true？

1. **测试系统**: 验证所有功能是否正常工作
2. **重新发送邮件**: 想要重新获取某个视频的摘要
3. **一次性使用**: 只想获取最新一个视频而不建立长期监控
4. **手动触发**: 通过GitHub Actions手动运行时使用

### GET_LATEST vs 正常模式

| 模式 | GET_LATEST=true | GET_LATEST=false (默认) |
|------|----------------|------------------------|
| **处理逻辑** | 总是处理最新视频 | 只处理未处理的新视频 |
| **数据存储** | 不保存处理状态 | 保存处理状态避免重复 |
| **使用场景** | 测试、重新发送 | 自动监控、定时任务 |
| **邮件频率** | 每次运行都发送 | 只有新视频才发送 |

## 🛠️ 高级配置

### 修改检查频率

编辑 `.github/workflows/youtube-monitor.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # 每6小时检查一次
```

### 切换字幕源

如果 downsub.com 不可用，可以切换回原始方法：

```bash
# 在 GitHub Secrets 中设置
USE_DOWNSUB=false
```

### 监控其他频道

虽然默认监控 @lidangzzz，但你也可以：

```bash
# 设置其他用户名
TARGET_USERNAME=other-channel-name

# 或者直接使用频道ID (作为备选)
CHANNELS_TO_MONITOR=UCxxxxxx,UCyyyyyy
```

## 🔍 故障排除

### 常见问题

1. **找不到频道ID**
   - 确认用户名拼写正确
   - 检查 YouTube API 配额
   - 验证频道是否公开

2. **DownSub.com 无法访问**
   - 设置 `USE_DOWNSUB=false` 切换到原始方法
   - 检查网络连接

3. **没有收到邮件**
   - 检查垃圾邮件文件夹
   - 验证 Gmail 应用密码
   - 确认已开启2FA

### 调试模式

```bash
export TEST_MODE="true"
python src/main.py
```

## 📊 监控数据

项目会在 `data/` 目录下保存：

- `processed_videos.json`: 已处理的视频记录
- `last_run_summary.json`: 最后运行摘要
- `transcripts/`: 视频字幕文件

## 🔒 安全性

- 所有API密钥通过 GitHub Secrets 安全存储
- 不在代码中暴露任何凭据
- 字幕通过HTTPS安全下载
- 数据存储在你自己的GitHub仓库中

---

**注意**: 这个配置专门为监控 @lidangzzz 频道优化，使用 downsub.com 确保最佳的字幕获取体验。