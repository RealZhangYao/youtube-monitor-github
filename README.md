# YouTube Monitor - GitHub Actions Edition

A free, automated YouTube channel monitoring system that runs entirely on GitHub Actions. Monitor multiple YouTube channels for new videos, get AI-generated summaries, and receive email notifications - all without any server costs!

## 🌟 Features

- 🎥 **Automatic YouTube Channel Monitoring** - Track multiple channels for new uploads
- 📝 **Transcript Extraction** - Automatically fetch video captions/subtitles
- 🤖 **AI-Powered Summaries** - Generate concise summaries using Google's Gemini AI
- 📧 **Email Notifications** - Get notified via Gmail when new videos are published
- 💾 **Data Persistence** - Store transcripts and history in your GitHub repo
- 💰 **Completely Free** - Runs on GitHub Actions free tier
- 🔄 **Scheduled Checks** - Runs every 6 hours (configurable)

## 🚀 Quick Start

### 1. Fork this Repository

Click the "Fork" button at the top right of this page to create your own copy.

### 2. Set up API Keys

You'll need three API keys (all free):

#### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy the API key

#### Google AI Studio (Gemini)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key

#### Gmail App Password
1. Enable [2-Factor Authentication](https://myaccount.google.com/security) on your Google account
2. Go to [App passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Copy the 16-character password

### 3. Configure GitHub Secrets

In your forked repository:
1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIza...` |
| `GEMINI_API_KEY` | Google AI Studio API key | `AIza...` |
| `GMAIL_USER` | Your Gmail address | `yourname@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail app password (no spaces) | `abcdabcdabcdabcd` |
| `RECIPIENT_EMAIL` | Email to receive notifications | `yourname@gmail.com` |
| `CHANNELS_TO_MONITOR` | Comma-separated channel IDs | `UCddiUEpeqJcYeBxX1IVBKvQ,UC_x5XG1OV2P6uZZ5FSM9Ttw` |

### 4. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. Click "I understand my workflows, go ahead and enable them"

### 5. Test the System

1. Go to Actions → YouTube Monitor
2. Click "Run workflow" → "Run workflow"
3. Check "Run in test mode" to verify all connections

## 📋 Finding YouTube Channel IDs

To find a channel ID:

**Method 1 - From Channel URL:**
- If URL is like `youtube.com/channel/UCxxxxx`, the ID is `UCxxxxx`

**Method 2 - View Page Source:**
1. Go to the YouTube channel page
2. Right-click → View Page Source
3. Search for `"channelId"`
4. Copy the value (starts with UC)

**Popular Channels to Test:**
- **The Verge**: `UCddiUEpeqJcYeBxX1IVBKvQ`
- **Google Developers**: `UC_x5XG1OV2P6uZZ5FSM9Ttw`
- **TED**: `UCAuUUnT6oDeKwE6v1NGQxug`

## 🔧 Configuration

### Scheduling

By default, the monitor runs every 6 hours. To change this, edit `.github/workflows/youtube-monitor.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

Common schedules:
- Every 3 hours: `'0 */3 * * *'`
- Every 12 hours: `'0 */12 * * *'`
- Daily at 9 AM: `'0 9 * * *'`
- Twice daily: `'0 9,21 * * *'`

### Manual Trigger

You can manually run the monitor anytime:
1. Go to Actions → YouTube Monitor
2. Click "Run workflow"

## 📁 Data Storage

The system stores data in your repository:

```
data/
├── processed_videos.json    # Track which videos have been processed
├── last_run_summary.json    # Summary of the last run
└── transcripts/            # Saved video transcripts
    └── [channel_id]/
        └── [video_id].json
```

## 📧 Email Format

You'll receive formatted HTML emails containing:
- Channel and video information
- AI-generated summary with key points
- Direct link to the video
- Timestamp of when it was processed

## 🛠️ Troubleshooting

### No emails received?
- Check spam folder
- Verify Gmail app password is correct (no spaces)
- Ensure 2FA is enabled on Gmail account
- Check Actions logs for errors

### API quota exceeded?
- YouTube API: 10,000 units/day (free)
- Reduce number of channels or check frequency
- Each check uses ~100 units per channel

### No transcript available?
- Some videos don't have captions
- Private or age-restricted videos may not work
- Check if video has CC button on YouTube

## 💰 Cost Analysis

**Completely FREE** when staying within limits:
- GitHub Actions: 2,000 minutes/month (this uses ~30 min/month)
- YouTube API: 10,000 units/day
- Gemini API: Generous free tier
- Gmail: 500 emails/day limit

## 🔒 Security

- All API keys stored as GitHub Secrets
- No credentials in code
- Data stored in your own repository
- Email sent via secure SMTP

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

Built with:
- GitHub Actions for automation
- YouTube Data API v3 for video data
- youtube-transcript-api for subtitles
- Google Gemini AI for summaries
- Gmail SMTP for notifications

---

Made with ❤️ for the YouTube content creator community