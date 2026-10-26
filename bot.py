#!/usr/bin/env python3
import os
import urllib.request
import xml.etree.ElementTree as ET
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Configuration ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TARGET_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# List of YouTube channels to monitor
CHANNELS = [
    {"name": "Mr. English", "id": "UCE1P_bsD_kKh-i0HEsPpxtA"},
    # Add more channels here:
    # {"name": "Channel Name", "id": "UCxxxxxxxxxxxxxxxxxxxxxx"},
]

# --- Helper Functions ---
def fetch_latest_video(channel_id: str):
    """Fetch the latest video from the YouTube RSS feed."""
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
    """Display the main menu with inline buttons."""
    keyboard = [
        [InlineKeyboardButton("📺 Latest Videos", callback_data='latest')],
        [InlineKeyboardButton("📋 Channel List", callback_data='list')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello! Welcome to the bot. Please choose an option below:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the help text."""
    help_text = (
        "**Bot Help:**\n\n"
        "/start - Show main menu\n"
        "/latest - Get the latest video from all channels\n"
        "/list - Show monitored channels\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send the latest video from each channel."""
    # Check if the update is from a button click or a text command
    message = update.message if update.message else update.callback_query.message
    await message.reply_text("Fetching latest videos... ⏳")
    
    for channel in CHANNELS:
        video = fetch_latest_video(channel["id"])
        if video:
            text = f"🎬 **{video['title']}**\n\n📺 Channel: {channel['name']}\n\n[Watch Video]({video['link']})"
            await message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=False)
        else:
            await message.reply_text(f"❌ No video found for channel {channel['name']}.")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the list of monitored channels."""
    message = update.message if update.message else update.callback_query.message
    text = "**📋 Monitored Channels:**\n\n"
    for channel in CHANNELS:
        text += f"- {channel['name']}\n"
    await message.reply_text(text, parse_mode='Markdown')

# --- Callback Query Handler ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button clicks."""
    query = update.callback_query
    await query.answer()

    if query.data == 'latest':
        await latest_command(update, context)
    elif query.data == 'list':
        await list_command(update, context)
    elif query.data == 'help':
        await help_command(update, context)

# --- Main Function ---
def main():
    """Start the bot."""
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not set.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("latest", latest_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
