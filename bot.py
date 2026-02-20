import os
import time
import requests
import subprocess
import logging
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 配置信息
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")
# 允许的 Chat IDs，用逗号分隔，通过环境变量传入
ALLOWED_CHAT_IDS_STR = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS = [int(x.strip()) for x in ALLOWED_CHAT_IDS_STR.split(",") if x.strip()]

API_URL = f"https://api.telegram.org/bot{TOKEN}"

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 60, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=70)
        return response.json()
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        logger.error(f"网络异常: {e}")
        return None

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    # Telegram 限制单条消息最多 4096 字符，若结果过长需分割
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        payload = {
            "chat_id": chat_id, 
            "text": text[i:i+chunk_size],
            "parse_mode": "Markdown" # 使用Markdown格式化代码块等
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"发送消息异常: {e}")

def run_claude_code(prompt):
    try:
        # 设置 NO_COLOR 防止输出乱码的 ANSI 控制字符
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        env["FORCE_COLOR"] = "0"
        
        # 调用 claude，使用 -p 运行单次指令
        cmd = ["claude", "-p", prompt]
        logger.info(f"Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=600 # 允许最长运行 10 分钟 (按需更改)
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            if output:
                return f"```\n{output}\n```"
            return "✅ 执行成功，但没有返回文本。"
        else:
            return f"❌ 执行出错 (Exit {result.returncode}):\n```\n{error}\n{output}\n```"
            
    except subprocess.TimeoutExpired:
        return "⚠️ 执行超时 (超过设置的上限时间 10 分钟)。"
    except Exception as e:
        return f"🚨 系统运行错误: {str(e)}"

def main():
    if not TOKEN or TOKEN == "your_bot_token_here":
        logger.error("请设置 TELEGRAM_BOT_TOKEN 环境变量")
        return
        
    if not ALLOWED_CHAT_IDS:
        logger.warning("未设置 ALLOWED_CHAT_IDS 环境变量，所有人都可以使用该 Bot！强烈建议设置主人的 Chat ID。")
        
    logger.info("🤖 Bot 正在运行中...")
    update_id = None
    
    while True:
        updates = get_updates(offset=update_id)
        if updates and updates.get("ok"):
            for item in updates.get("result", []):
                update_id = item["update_id"] + 1
                msg = item.get("message", {})
                
                if "text" in msg:
                    chat_id = msg["chat"]["id"]
                    user_text = msg["text"]
                    
                    logger.info(f"收到来自 {chat_id} 的消息: {user_text}")
                    
                    # 鉴权
                    if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
                        logger.warning(f"鉴权失败，未授权的 User: {chat_id}")
                        send_message(chat_id, f"🚫 鉴权失败，未授权的用户 (您的 Chat ID: `{chat_id}`)")
                        continue
                        
                    send_message(chat_id, "⏳ 正在让 Claude 思考并执行中，请稍候...")
                    
                    # 运行 Claude
                    response = run_claude_code(user_text)
                    send_message(chat_id, response)
        
        # 避免过于频繁的重试导致 CPU 占用或封禁
        time.sleep(1)

if __name__ == '__main__':
    main()
