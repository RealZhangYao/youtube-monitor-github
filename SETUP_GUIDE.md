# YouTube Monitor Setup Guide

## Step-by-Step Setup Instructions

### 1. Create Your GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the "+" icon → "New repository"
3. Name: `youtube-monitor` (or any name you prefer)
4. Make it Public or Private (both work)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### 2. Push This Code to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR-USERNAME/youtube-monitor.git

# Push the code
git push -u origin master
```

### 3. Get Required API Keys

#### YouTube Data API v3 (Free)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. In the menu, go to "APIs & Services" → "Library"
4. Search for "YouTube Data API v3"
5. Click on it and press "Enable"
6. Go to "APIs & Services" → "Credentials"
7. Click "Create Credentials" → "API Key"
8. Copy the API key

#### Google AI Studio - Gemini API (Free)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Select "Create API key in new project"
5. Copy the API key

#### Gmail App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" (required)
3. After enabling 2FA, go to [App passwords](https://myaccount.google.com/apppasswords)
4. Select app: "Mail"
5. Select device: "Other" → Type "YouTube Monitor"
6. Click "Generate"
7. Copy the 16-character password (save it, you can't see it again!)

### 4. Configure GitHub Secrets

In your GitHub repository:

1. Go to "Settings" tab
2. In the left sidebar, click "Secrets and variables" → "Actions"
3. Click "New repository secret" for each:

| Secret Name | Value |
|------------|-------|
| `YOUTUBE_API_KEY` | Your YouTube API key from step 3 |
| `GEMINI_API_KEY` | Your Gemini API key from step 3 |
| `GMAIL_USER` | Your Gmail address (e.g., yourname@gmail.com) |
| `GMAIL_APP_PASSWORD` | The 16-character app password (no spaces) |
| `RECIPIENT_EMAIL` | Email to receive notifications |
| `CHANNELS_TO_MONITOR` | Channel IDs separated by commas |

### 5. Finding YouTube Channel IDs

**Method 1 - From URL:**
- If channel URL is `youtube.com/channel/UCxxxxx`
- The channel ID is `UCxxxxx`

**Method 2 - From @handle:**
1. Go to the channel page (e.g., youtube.com/@MrBeast)
2. Right-click → "View Page Source"
3. Press Ctrl+F (or Cmd+F on Mac)
4. Search for `"channelId"`
5. Copy the value that starts with "UC"

**Popular channels to test:**
- MrBeast: `UCX6OQ3DkcsbYNE6H8uQQuVA`
- The Verge: `UCddiUEpeqJcYeBxX1IVBKvQ`
- TED: `UCAuUUnT6oDeKwE6v1NGQxug`

### 6. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. You should see "YouTube Monitor" workflow
3. Click "Enable workflow" if prompted

### 7. Test the System

1. Go to "Actions" tab
2. Click "YouTube Monitor" in the left sidebar
3. Click "Run workflow" button
4. Check "Run in test mode"
5. Click green "Run workflow" button
6. Wait for it to complete (takes ~1 minute)
7. Click on the run to see logs

### 8. Verify Everything Works

If successful, you should see:
- ✓ YouTube API connection successful
- ✓ Gemini AI connection successful  
- ✓ Gmail SMTP connection successful
- ✓ Data Store operational

### 9. First Real Run

1. Uncheck "Run in test mode"
2. Click "Run workflow" again
3. Check your email for notifications!

## Troubleshooting

### "YouTube API connection failed"
- Verify your API key is correct
- Check if YouTube Data API v3 is enabled in Google Cloud Console
- Make sure you haven't exceeded the daily quota (10,000 units)

### "Gmail SMTP connection failed"
- Ensure 2-Factor Authentication is enabled
- Verify app password is correct (16 characters, no spaces)
- Try generating a new app password
- Check if "Less secure app access" needs to be enabled

### "No new videos found"
- This is normal if channels haven't posted recently
- Check `data/processed_videos.json` to see what's been processed
- Delete this file to reprocess all videos

### Email not received
- Check spam/junk folder
- Verify RECIPIENT_EMAIL is correct
- Check GitHub Actions logs for errors

## Customization

### Change Check Frequency
Edit `.github/workflows/youtube-monitor.yml`:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

### Add More Channels
Update the `CHANNELS_TO_MONITOR` secret with comma-separated channel IDs

### Modify Email Template
Edit `src/email_sender.py` to customize the email format

## Data Storage

All data is stored in your repository:
- `data/processed_videos.json` - Tracks processed videos
- `data/transcripts/` - Saved video transcripts
- `data/last_run_summary.json` - Summary of last run

## Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Verify all secrets are set correctly
3. Test with a single channel first
4. Create an issue in the repository

Happy monitoring! 🎥