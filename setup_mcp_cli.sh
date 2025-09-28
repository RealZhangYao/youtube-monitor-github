#!/bin/bash

# Setup GitHub MCP Server for Claude Code CLI

echo "=== GitHub MCP Server Setup for Claude Code CLI ==="
echo ""

# Source the environment variables
source ~/.zshrc

# Check if GitHub PAT is set
if [ -z "$GITHUB_PAT" ]; then
    echo "❌ GITHUB_PAT not found in environment"
    echo "   Please add to ~/.zshrc: export GITHUB_PAT='your_pat_here'"
    exit 1
fi

echo "✅ GitHub PAT found in environment"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Pull the Docker image
echo ""
echo "📦 Pulling GitHub MCP Server Docker image..."
docker pull ghcr.io/github/github-mcp-server

# Configure MCP for Claude Code CLI
echo ""
echo "⚙️  Configuring Claude Code CLI MCP..."

# Option 1: Remote Server Setup (if available)
# echo "Trying remote server setup..."
# claude mcp add --transport http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer $GITHUB_PAT"

# Option 2: Local Docker Setup
echo "Setting up local Docker MCP server..."
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PAT" -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server

echo ""
echo "✅ MCP configuration complete!"
echo ""
echo "🔍 Verifying installation..."
claude mcp list

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart your terminal or run: source ~/.zshrc"
echo "2. Use /mcp command in Claude Code to access GitHub tools"
echo ""
echo "Example commands to test:"
echo "- /mcp list_repositories"
echo "- /mcp get_workflow_runs --repo youtube-monitor-github"
echo "- /mcp trigger_workflow --repo youtube-monitor-github --workflow youtube-monitor.yml"