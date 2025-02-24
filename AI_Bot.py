import logging
import os
import tempfile
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from gtts import gTTS
from pytube import YouTube
from deep_translator import GoogleTranslator 
from forex_python.converter import CurrencyRates
import replicate

# Bot Configuration
TOKEN = "7931988436:AAFb7tpH8gSoiDeVgNZ7CMHr0ncyg0lAV9M"
NEWS_API_KEY = "0a4ecfaeab1943fa9d3546bee74d4fd9"
REPLICATE_API_KEY = "r8_OAjePwF4K85gbUr3nwjA0w03NY3RB0i2vr3aD"

replicate.client = replicate.Client(api_token=REPLICATE_API_KEY)

# Initialize bot
bot = Bot(token=TOKEN)
currency_rates = CurrencyRates()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Chatbot function
def ai_chat(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("AI Chat is under development.")

# News Summarizer
def news(update: Update, context: CallbackContext) -> None:
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:3]
    news_text = "\n".join([f"{i+1}. {a.get('title', 'No Title Available')}" for i, a in enumerate(articles)])
    update.message.reply_text(news_text if news_text.strip() else "⚠️ No news available right now.")

# YouTube Video Downloader
def download_youtube(update: Update, context: CallbackContext) -> None:
    video_url = context.args[0]
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download()
    update.message.reply_text("Downloaded successfully!")

# Text-to-Speech (gTTS)
def text_to_speech(update: Update, context: CallbackContext) -> None:
    text = " ".join(context.args)
    if not text:
        update.message.reply_text("Usage: /tts <text>")
        return
    
    tts = gTTS(text=text, lang="en")
    temp_path = tempfile.gettempdir() + "/output.mp3"
    tts.save(temp_path)
    with open(temp_path, "rb") as audio_file:
        update.message.reply_voice(voice=audio_file)
    os.remove(temp_path)

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
        output = replicate.run("stability-ai/stable-diffusion", input={"prompt": prompt})
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
