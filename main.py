import sys
try:
    import audioop
except ModuleNotFoundError:
    import audioop_lts
    sys.modules['audioop'] = audioop_lts

import disnake
from disnake.ext import commands
import asyncio
import os
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1041431136687112196
BURMALDA_URL = "https://www.youtube.com/watch?v=5h84DVeMom4"

COOKIES_TEXT = os.getenv("YT_COOKIES")
COOKIE_FILE_PATH = os.path.join(os.getcwd(), "runtime_cookies.txt")

if COOKIES_TEXT:
    with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(COOKIES_TEXT)

intents = disnake.Intents.default()
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

if os.path.exists(COOKIE_FILE_PATH):
    YDL_OPTIONS['cookiefile'] = COOKIE_FILE_PATH

async def keep_playing(vc):
    while vc.is_connected():
        if not vc.is_playing():
            try:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(BURMALDA_URL, download=False)
                    direct_audio_url = info['url']

                source = disnake.FFmpegPCMAudio(
                    direct_audio_url, 
                    before_options=FFMPEG_OPTIONS['before_options'], 
                    options=FFMPEG_OPTIONS['options']
                )
                vc.play(source)
                print("Успешно запустили поток Бурмалды!")
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен 24/7 на стабильном движке!")
    await asyncio.sleep(5)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=30.0, reconnect=True)
            bot.loop.create_task(keep_playing(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(15)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect(timeout=30.0, reconnect=True)
                bot.loop.create_task(keep_playing(vc))
            except Exception:
                pass

bot.run(TOKEN)
