import sys
try:
    import audioop
except ModuleNotFoundError:
    import audioop_lts
    sys.modules['audioop'] = audioop_lts  # Хитрый трюк: подменяем модуль для Python 3.13

import discord
from discord.ext import commands
import asyncio
import os
import yt_dlp


TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1041431136687112196
BURMALDA_URL = "https://www.youtube.com/watch?v=5h84DVeMom4"

# Достаем куки из секретных переменных Railway и создаем временный файл на сервере
COOKIES_TEXT = os.getenv("YT_COOKIES")
COOKIE_FILE_PATH = "runtime_cookies.txt"

if COOKIES_TEXT:
    with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(COOKIES_TEXT)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}

# Если куки успешно создались, добавляем их в настройки yt-dlp
if os.path.exists(COOKIE_FILE_PATH):
    YDL_OPTIONS['cookiefile'] = COOKIE_FILE_PATH

async def keep_playing(vc):
    while vc.is_connected():
        if not vc.is_playing():
            try:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(BURMALDA_URL, download=False)
                    direct_audio_url = info['url']

                source = discord.FFmpegPCMAudio(
                    direct_audio_url, 
                    before_options=FFMPEG_OPTIONS['before_options'], 
                    options=FFMPEG_OPTIONS['options']
                )
                vc.play(source)
                print("Успешно запустили поток Бурмалды с куками!")
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен 24/7 с поддержкой YouTube!")
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect()
            bot.loop.create_task(keep_playing(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(5)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect()
                bot.loop.create_task(keep_playing(vc))
            except Exception:
                pass

bot.run(TOKEN)
