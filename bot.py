#!/usr/bin/env python3
import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Configuration ---
# این مقادیر از GitHub Secrets خوانده می‌شوند
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# آیدی چت یا کانالی که ربات باید آخرین ویدیوها را آنجا بفرستد (اختیاری)
TARGET_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") 

# لیست کانال‌های یوتیوب (می‌توانید از فایل channels.txt بخوانید)
CHANNELS = [
    {"name": "Mr. English", "id": "UCE1P_bsD_kKh-i0HEsPpxtA"},
    {"name": "کانال دوم", "id": "UCxxxxxxxxxxxxxxxxxxxxxx"}, # آیدی کانال دوم را اینجا بگذارید
]

# --- Helper Functions ---
def fetch_latest_video(channel_id: str):
    """آخرین ویدیو را از فید RSS یوتیوب می‌گیرد."""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        entry = root.find('atom:entry', ns)
        if entry is not None:
            title = entry.find('atom:title', ns).text
            link = entry.find('atom:link', ns).attrib['href']
            video_id = entry.find('yt:videoId', ns).text
            return {"title": title, "link": link, "id": video_id}
    except Exception as e:
        print(f"Error fetching {channel_id}: {e}")
    return None

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی را با دکمه‌های شیشه‌ای نمایش می‌دهد."""
    keyboard = [
        [InlineKeyboardButton("📺 آخرین ویدیوها", callback_data='latest')],
        [InlineKeyboardButton("📋 لیست کانال‌ها", callback_data='list')],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! به ربات خوش آمدید. یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """متن راهنما را ارسال می‌کند."""
    help_text = (
        "**راهنمای ربات:**\n\n"
        "/start - نمایش منوی اصلی\n"
        "/latest - دریافت آخرین ویدیو از تمام کانال‌ها\n"
        "/list - نمایش لیست کانال‌های تحت نظر\n"
        "/help - نمایش این راهنما"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """آخرین ویدیو را از هر کانال دریافت و ارسال می‌کند."""
    await update.message.reply_text("در حال دریافت آخرین ویدیوها... ⏳")
    for channel in CHANNELS:
        video = fetch_latest_video(channel["id"])
        if video:
            text = f"🎬 **{video['title']}**\n\n📺 کانال: {channel['name']}\n\n[مشاهده ویدیو]({video['link']})"
            await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=False)
        else:
            await update.message.reply_text(f"❌ ویدیویی برای کانال {channel['name']} یافت نشد.")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لیست کانال‌های تحت نظر را نمایش می‌دهد."""
    text = "**📋 کانال‌های تحت نظر:**\n\n"
    for channel in CHANNELS:
        text += f"- {channel['name']}\n"
    await update.message.reply_text(text, parse_mode='Markdown')

# --- Callback Query Handler (برای دکمه‌های شیشه‌ای) ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دکمه‌های شیشه‌ای را مدیریت می‌کند."""
    query = update.callback_query
    await query.answer() # به تلگرام اطلاع می‌دهد که کلیک دریافت شده است

    if query.data == 'latest':
        await latest_command(update, context)
    elif query.data == 'list':
        await list_command(update, context)
    elif query.data == 'help':
        await help_command(update, context)

# --- Main Function ---
def main():
    """ربات را راه‌اندازی می‌کند."""
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not set.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # ثبت هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("latest", latest_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
