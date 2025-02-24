import logging
import os
import tempfile
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from gtts import gTTS
from pytube import YouTube
from deep_translator import GoogleTranslator
from forex_python.converter import CurrencyRates
import replicate

# Bot Configuration
TOKEN = os.getenv("TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

replicate.client = replicate.Client(api_token=REPLICATE_API_KEY)
currency_rates = CurrencyRates()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Chatbot function
async def ai_chat(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("AI Chat is under development.")

# News Summarizer
async def news(update: Update, context: CallbackContext) -> None:
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:3]
    news_text = "\n".join([f"{i+1}. {a.get('title', 'No Title Available')}" for i, a in enumerate(articles)])
    await update.message.reply_text(news_text if news_text.strip() else "⚠️ No news available right now.")

# YouTube Video Downloader
async def download_youtube(update: Update, context: CallbackContext) -> None:
    video_url = context.args[0]
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download()
    await update.message.reply_text("Downloaded successfully!")

# Text-to-Speech (gTTS)
async def text_to_speech(update: Update, context: CallbackContext) -> None:
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /tts <text>")
        return
    
    tts = gTTS(text=text, lang="en")
    temp_path = tempfile.gettempdir() + "/output.mp3"
    tts.save(temp_path)
    with open(temp_path, "rb") as audio_file:
        await update.message.reply_voice(voice=audio_file)
    os.remove(temp_path)

# Text Translator
async def translate_text(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /translate <target_language> <text>")
        return
    target_language = args[0]
    text_to_translate = " ".join(args[1:])
    translated_text = GoogleTranslator(source="auto", target=target_language).translate(text_to_translate)
    await update.message.reply_text(f"Translated: {translated_text}")

# Currency Converter
async def currency_convert(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /convert <amount> <from_currency> <to_currency>")
        return
    amount, from_currency, to_currency = args[0], args[1].upper(), args[2].upper()
    try:
        converted_amount = currency_rates.convert(from_currency, to_currency, float(amount))
        await update.message.reply_text(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Conversion error: {str(e)}")

# Free Image Generation using Replicate API
async def generate_image(update: Update, context: CallbackContext) -> None:
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Usage: /image <description>")
        return
    try:
        output = replicate.run("stability-ai/stable-diffusion", input={"prompt": prompt})
        await update.message.reply_photo(photo=output[0])
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error generating image: {str(e)}")

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I'm your AI Bot! 🤖")

# Main function
def main():
    application = Application.builder().token(TOKEN).build()

    # Adding command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat", ai_chat))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("youtube", download_youtube))
    application.add_handler(CommandHandler("tts", text_to_speech))
    application.add_handler(CommandHandler("translate", translate_text))
    application.add_handler(CommandHandler("convert", currency_convert))
    application.add_handler(CommandHandler("image", generate_image))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
