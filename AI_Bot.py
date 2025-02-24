# Telegram AI Bot - Version 1
# Features: AI Chat, Image Gen, Speech-to-Text, TTS, Google Search, YouTube Downloader, News, Coding, Currency Converter, etc.
# Deployable on Railway.app

import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import g4f
import requests
from pytube import YouTube
from deep_translator import GoogleTranslator 
import speech_recognition as sr
import pyttsx3
from forex_python.converter import CurrencyRates
from PIL import Image
import io
import base64
import replicate

# Bot Configuration
TOKEN = "7931988436:AAFb7tpH8gSoiDeVgNZ7CMHr0ncyg0lAV9M"  # Replace with your actual Telegram bot token
NEWS_API_KEY = "0a4ecfaeab1943fa9d3546bee74d4fd9"  # Replace with your News API key
import replicate

REPLICATE_API_KEY = "r8_OAjePwF4K85gbUr3nwjA0w03NY3RB0i2vr3aD"  # Replace this with your actual key

replicate.client = replicate.Client(api_token=REPLICATE_API_KEY)  # Set the API key globally



# Initialize bot
bot = Bot(token=TOKEN)
translator = GoogleTranslator(source="auto", target="en")
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
currency_rates = CurrencyRates()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Chatbot function
def ai_chat(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",  # You can use "gpt-3.5-turbo" as well
            messages=[{"role": "user", "content": user_message}]
        )
        update.message.reply_text(response)
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}. Please try again later.")

# News Summarizer
def news(update: Update, context: CallbackContext) -> None:
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:3]
    news_text = "\n".join([f"{i+1}. {a.get('title', 'No Title Available')}" for i, a in enumerate(articles)])
    if not news_text.strip():
        update.message.reply_text("⚠️ No news available right now. Try again later.")
    else:
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

# Text Translator
def translate_text(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /translate <target_language> <text>")
        return
    target_language = args[0]
    text_to_translate = " ".join(args[1:])
    translated_text = GoogleTranslator(source="auto", target=target_language).translate(text_to_translate)
    update.message.reply_text(f"Translated: {translated_text}")

# Currency Converter
def currency_convert(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 3:
        update.message.reply_text("Usage: /convert <amount> <from_currency> <to_currency>")
        return
    amount, from_currency, to_currency = args[0], args[1].upper(), args[2].upper()
    try:
        converted_amount = currency_rates.convert(from_currency, to_currency, float(amount))
        update.message.reply_text(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
    except Exception as e:
        update.message.reply_text(f"⚠️ Conversion error: {str(e)}")

# Free Image Generation using Replicate API
def generate_image(update: Update, context: CallbackContext) -> None:
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("Usage: /image <description>")
        return

    try:
        output = replicate.run(
            "stability-ai/stable-diffusion",
            input={"prompt": prompt}
        )
        update.message.reply_photo(photo=output[0])
    except Exception as e:
        update.message.reply_text(f"⚠️ Error generating image: {str(e)}")


# Command Handlers
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Hello! I'm your AI Bot!")))
    dp.add_handler(CommandHandler("chat", ai_chat))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("youtube", download_youtube))
    dp.add_handler(CommandHandler("tts", text_to_speech))
    dp.add_handler(CommandHandler("translate", translate_text))
    dp.add_handler(CommandHandler("convert", currency_convert))
    dp.add_handler(CommandHandler("image", generate_image))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
