#!/bin/bash

# 部署脚本 (在 EC2 实例中运行)

set -e

APP_DIR="/home/ubuntu/claude_bot"

echo "🔧 开始部署 Claude Telegram Bot..."

# 安装依赖
echo "📦 安装 Python 依赖..."
sudo apt update
sudo apt install -y python3-pip
pip3 install -r requirements.txt

# 创建目录（如果不存在）
mkdir -p "$APP_DIR"
cp bot.py requirements.txt claude-bot.service "$APP_DIR/"

# 配置 Systemd 守护进程
echo "⚙️ 配置 Systemd 服务..."
# 提示用户修改文件中的 TOKEN 
echo "⚠️ 请确保已在 $APP_DIR/claude-bot.service 中配置了 TELEGRAM_BOT_TOKEN 和 ALLOWED_CHAT_IDS！"

sudo cp "$APP_DIR/claude-bot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable claude-bot
sudo systemctl restart claude-bot

echo "✅ 部署完成！"
echo "👉 你可以使用该命令查看运行日志：sudo journalctl -u claude-bot -f"
