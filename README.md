# Claude Telegram Bot for EC2

这个项目运行一个极简的、常驻于 EC2 等服务器后台的 Telegram Bot。它可以通过 Telegram 消息直接调用服务器上的 `claude code` 命令，并将执行结果返回给你。

## 文件说明

- `bot.py`: Telegram Bot 的核心代码，使用 Long Polling (长轮询)获取消息。
- `requirements.txt`: 运行该脚本需要的 Python 库。
- `claude-bot.service`: Linux systemd 的服务守护配置文件。
- `deploy.sh`: 在目标服务器(如 EC2)上的辅助部署脚本。

## 部署说明 (到 EC2)

1. 克隆 / 上传本仓库代码到你的 EC2 (例如放到 `/home/ubuntu/claude_bot`)。
2. 确保你的 EC2 服务器**已经安装且登录了 Claude Code** (`npm install -g @anthropic-ai/claude-code` 然后运行 `claude login`)。
3. 编辑 `claude-bot.service` 文件：
   - 将 `TELEGRAM_BOT_TOKEN` 修改为你自己的 Bot Token (向 @BotFather 获取)。
   - 将 `ALLOWED_CHAT_IDS` 修改为你自己的 Telegram Chat ID (可以通过向机器人发送消息然后在终端查看，或者使用 @userinfobot 获取)。
   - 确认 `User`, `WorkingDirectory` 和 `PATH` 环境变量符合你服务器的设置。
4. 运行 `chmod +x deploy.sh` 赋予部署脚本执行权限。
5. 执行 `./deploy.sh`。

## 手动管理服务

- **查看运行日志**：`sudo journalctl -u claude-bot -f`
- **重启服务**：`sudo systemctl restart claude-bot`
- **停止服务**：`sudo systemctl stop claude-bot`
