# Claude Code CLI - GitHub MCP 配置指南

本指南帮助你在 Claude Code CLI 中配置 GitHub MCP Server。

## 前置要求

1. **Claude Code CLI** - 已安装并配置
2. **Docker Desktop** - 必须安装并运行
3. **GitHub PAT** - 已创建并添加到环境变量

## 快速开始

### 1. 环境变量已配置

你的 GitHub PAT 已经添加到 `~/.zshrc`：
```bash
export GITHUB_PAT="your_github_personal_access_token_here"
```

### 2. 运行设置脚本

```bash
# 重新加载环境变量
source ~/.zshrc

# 运行设置脚本
./setup_mcp_cli.sh
```

### 3. 手动配置（如果脚本失败）

#### 选项 A: 远程服务器（推荐，如果支持）
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer $GITHUB_PAT"
```

#### 选项 B: 本地 Docker
```bash
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PAT" -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

## 使用 MCP

### 查看配置的 MCP 服务器
```bash
claude mcp list
```

### 查看特定服务器详情
```bash
claude mcp get github
```

### 在 Claude Code 中使用

使用 `/mcp` 命令访问 GitHub 功能：

```
/mcp list_repositories
/mcp get_workflow_runs --owner RealZhangYao --repo youtube-monitor-github
/mcp trigger_workflow --owner RealZhangYao --repo youtube-monitor-github --workflow_id youtube-monitor.yml
```

## 实用示例

### 1. 触发测试模式工作流
```
/mcp trigger_workflow --owner RealZhangYao --repo youtube-monitor-github --workflow_id youtube-monitor.yml --ref master --inputs '{"test_mode": "true"}'
```

### 2. 获取最近的工作流运行
```
/mcp get_workflow_runs --owner RealZhangYao --repo youtube-monitor-github --per_page 5
```

### 3. 获取特定运行的日志
```
/mcp get_workflow_run_logs --owner RealZhangYao --repo youtube-monitor-github --run_id <RUN_ID>
```

### 4. 分析失败的运行
使用自然语言：
```
请分析 youtube-monitor-github 仓库最近失败的工作流，告诉我错误原因
```

## 配置范围

Claude Code CLI 支持三种配置范围：

1. **local**（默认）- 仅当前项目
2. **project** - 通过 `.mcp.json` 文件共享
3. **user** - 所有项目可用

设置全局可用：
```bash
claude mcp add -s user github -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PAT" -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

## 故障排除

### MCP 命令不可用
1. 确保你在项目目录中运行 Claude Code
2. 重启终端或运行 `source ~/.zshrc`
3. 验证配置：`claude mcp list`

### Docker 错误
```
docker: Cannot connect to the Docker daemon
```
解决：启动 Docker Desktop

### 权限错误
确保你的 GitHub PAT 有正确的权限：
- `repo` - 完整的仓库访问
- `workflow` - 工作流权限（如果需要触发）

### 查看日志
```bash
# Claude Code 日志位置
ls ~/.claude/logs/
```

## 删除 MCP 配置

如果需要重新配置：
```bash
claude mcp remove github
```

## 安全提示

1. GitHub PAT 已经在你的 `.zshrc` 中，注意保护这个文件
2. 不要在公共仓库中分享你的 PAT
3. 定期轮换 PAT
4. 使用最小必要权限

## 常用 MCP 命令参考

| 命令 | 描述 |
|------|------|
| `list_repositories` | 列出你的仓库 |
| `get_repository` | 获取仓库详情 |
| `list_workflow_runs` | 列出工作流运行 |
| `get_workflow_run` | 获取特定运行详情 |
| `get_workflow_run_logs` | 获取运行日志 |
| `trigger_workflow_dispatch` | 触发工作流 |
| `create_issue` | 创建 issue |
| `list_issues` | 列出 issues |
| `create_pull_request` | 创建 PR |

更多命令请参考官方文档或使用 `/mcp help` 查看。