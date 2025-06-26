import telebot
import requests
import time
import json
from datetime import datetime, timedelta
import logging
from telebot import types
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot initialization
bot = telebot.TeleBot("7908526504:AAH9XCXoshD-ttPu8Q-Hj5rOQNW8Zt9ryUw")
ALLOWED_GROUP_ID = -1002352923608
API_BASE = "http://168.231.113.96:9803"
PLAYER_INFO_API = "https://zoroinfomain.vercel.app/player_info"
API_KEY = "Fox-7CdxP"
CHANNEL_LINK = "https://t.me/NGALLBOTS"
CHANNEL_ID = "-1002388382340"
OWNER_ID = 7998175954

user_usage = {}
vip_users = set()
used_player_ids = set()
fr_locked = False

def load_data():
    global vip_users, used_player_ids
    try:
        with open('vip_users.txt', 'r') as f:
            vip_users = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        vip_users = set()
    try:
        with open('used_player_ids.txt', 'r') as f:
            used_player_ids = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        used_player_ids = set()

def save_data():
    with open('vip_users.txt', 'w') as f:
        json.dump(list(vip_users), f)
    with open('used_player_ids.txt', 'w') as f:
        json.dump(list(used_player_ids), f)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_vip(user_id):
    return user_id in vip_users or is_owner(user_id)

def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Membership check failed: {e}")
        return False

def can_user_request(user_id):
    if is_owner(user_id): 
        return True
    now = datetime.now()
    if user_id not in user_usage:
        user_usage[user_id] = {'count': 0, 'last_reset': now}
    if now - user_usage[user_id]['last_reset'] > timedelta(days=1):
        user_usage[user_id]['count'] = 0
        user_usage[user_id]['last_reset'] = now
    max_requests = 10 if is_vip(user_id) else 3
    return user_usage[user_id]['count'] < max_requests

def increment_user_count(user_id):
    if user_id in user_usage and not is_owner(user_id):
        user_usage[user_id]['count'] += 1
        logger.info(f"User {user_id} request count: {user_usage[user_id]['count']}")

def player_id_used_today(player_id):
    return player_id in used_player_ids

def add_player_id_to_used(player_id):
    used_player_ids.add(player_id)
    save_data()

def clear_daily_data():
    while True:
        now = datetime.now()
        # Clear at midnight
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(days=1)
        seconds_until_midnight = (tomorrow - now).total_seconds()
        time.sleep(seconds_until_midnight)
        
        global used_player_ids
        used_player_ids = set()
        save_data()
        logger.info("Daily player ID data cleared")

def check_api_health():
    try:
        url = f"{API_BASE}/get_time/12194912428"
        res = requests.get(url, timeout=5)
        return res.status_code < 500
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return False

def add_player(player_id):
    try:
        url = f"{API_BASE}/add_uid?uid={player_id}&time=86400&type=seconds"
        res = requests.get(url, timeout=10)
        return res.status_code == 200
    except Exception as e:
        logger.error(f"Failed to add player: {e}")
        return False

def get_player_info(player_id):
    try:
        url = f"{PLAYER_INFO_API}?uid={player_id}&key={API_KEY}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
        logger.warning(f"Player not found: {player_id}")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch player info: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    help_text = """
<b>🤖 Bot Commands:</b>

/add <PlayerID> - Add a player for 24 hours
/status - Check bot status
/vip - VIP management (owner only)
/frlock - Lock bot to VIP only (owner only)
/funlock - Unlock bot for all users (owner only)

🔹 Regular users: 3 requests/day
🔸 VIP users: 10 requests/day
"""
    bot.reply_to(message, help_text, parse_mode='HTML')

@bot.message_handler(commands=['frlock'])
def handle_frlock(message):
    if not is_owner(message.from_user.id): 
        return
    global fr_locked
    fr_locked = True
    bot.reply_to(message, "🔒 Bot locked to VIP and owner only.")

@bot.message_handler(commands=['funlock'])
def handle_funlock(message):
    if not is_owner(message.from_user.id): 
        return
    global fr_locked
    fr_locked = False
    bot.reply_to(message, "🔓 Bot unlocked for all users.")

@bot.message_handler(commands=['status'])
def handle_status(message):
    if fr_locked and not is_vip(message.from_user.id): 
        return
    api_status = "🟢 Online" if check_api_health() else "🔴 Offline"
    status_text = f"""
⚙️ <b>Bot Status</b>

API Status: {api_status}
VIP Users: {len(vip_users)}
Today's Players: {len(used_player_ids)}
Channel: @{CHANNEL_ID}
Bot Lock Status: {'🔒 Locked (VIP only)' if fr_locked else '🔓 Unlocked'}
"""
    bot.reply_to(message, status_text, parse_mode='HTML')

@bot.message_handler(commands=['add'])
def handle_add(message):
    user_id = message.from_user.id
    if fr_locked and not is_vip(user_id): 
        return
    if message.chat.id != ALLOWED_GROUP_ID: 
        return
    if not is_owner(user_id) and not is_member(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel", url=CHANNEL_LINK))
        bot.reply_to(message, "❌ You must join the channel first.", reply_markup=markup)
        return
    if not can_user_request(user_id):
        bot.reply_to(message, "❌ You reached the daily limit.")
        return
    try:
        player_id = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Usage: /add <PlayerID>")
        return
    if player_id_used_today(player_id):
        bot.reply_to(message, "⚠️ This ID was already used today.")
        return
    player_info = get_player_info(player_id)
    if not player_info:
        bot.reply_to(message, "❌ Player not found or API error.")
        return
    if add_player(player_id):
        increment_user_count(user_id)
        add_player_id_to_used(player_id)
        bot.reply_to(message, f"✅ Added player {player_info.get('player_name', 'Unknown')} ({player_id}) for 24h")

@bot.message_handler(commands=['vip'])
def handle_vip(message):
    user_id = message.from_user.id
    if not is_owner(user_id): 
        return
    parts = message.text.split()
    if len(parts) == 3:
        action = parts[1].lower()
        target_id = int(parts[2])
        if action == "add":
            vip_users.add(target_id)
            bot.reply_to(message, f"✅ User {target_id} added to VIP.")
        elif action == "remove":
            vip_users.discard(target_id)
            bot.reply_to(message, f"✅ User {target_id} removed from VIP.")
        save_data()
    else:
        vip_list = "\n".join(str(uid) for uid in vip_users)
        bot.reply_to(message, f"<b>VIP List:</b>\n<code>{vip_list or 'No VIP users yet'}</code>", parse_mode='HTML')

if __name__ == '__main__':
    load_data()
    logger.info("Data loaded successfully")
    threading.Thread(target=clear_daily_data, daemon=True).start()
    if check_api_health():
        logger.info("API is reachable")
    else:
        logger.warning("API is not reachable")
    logger.info("Starting bot...")
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(10)