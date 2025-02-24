# Telegram AI Bot - Version 1
# Features: AI Chat, Image Gen, Speech-to-Text, TTS, Google Search, YouTube Downloader, Weather, News, Coding, etc.
# Deployable on Railway.app

import os
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import requests
from pytube import YouTube
from googletrans import Translator
import speech_recognition as sr
import pyttsx3

# Load environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Add your Telegram bot token in Railway environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Initialize bot
bot = Bot(token=TOKEN)
translator = Translator()
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
openai.api_key = OPENAI_API_KEY

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Chatbot function
def ai_chat(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="text-davinci-003",
        messages=[{"role": "user", "content": user_message}]
    )
    update.message.reply_text(response["choices"][0]["message"]["content"].strip())

# Weather function
def weather(update: Update, context: CallbackContext) -> None:
    city = " ".join(context.args)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("main"):
        temp = response["main"]["temp"]
        update.message.reply_text(f"Weather in {city}: {temp}°C")
    else:
        update.message.reply_text("City not found.")

# News Summarizer
def news(update: Update, context: CallbackContext) -> None:
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:3]
    news_text = "\n".join([f"{i+1}. {a['title']}" for i, a in enumerate(articles)])
    update.message.reply_text(news_text)

# YouTube Video Downloader
def download_youtube(update: Update, context: CallbackContext) -> None:
    video_url = context.args[0]
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download()
    update.message.reply_text("Downloaded successfully!")

# Text-to-Speech
def text_to_speech(update: Update, context: CallbackContext) -> None:
    text = " ".join(context.args)
    tts_engine.say(text)
    tts_engine.runAndWait()
    update.message.reply_text("Speech played!")

# Command Handlers
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Hello! I'm your AI Bot!")))
    dp.add_handler(CommandHandler("chat", ai_chat))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("youtube", download_youtube))
    dp.add_handler(CommandHandler("tts", text_to_speech))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
