import discord
from discord.ext import commands
import asyncio
import os
import yt_dlp  # Добавили библиотеку для работы с YouTube

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1041431136687112196 
# Твоя ссылка на трансляцию Бурмалды с YouTube
BURMALDA_URL = "https://www.youtube.com/watch?v=5h84DVeMom4"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Настройки для скачивания звука из YouTube
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}

async def keep_playing(vc):
    """Бесконечно удерживает поток активным из YouTube"""
    while vc.is_connected():
        if not vc.is_playing():
            try:
                # Определяем систему (для сервера — ffmpeg)
                exe_name = 'ffmpeg.exe' if os.name != 'nt' else 'ffmpeg'
                
                # Достаем прямую аудиоссылку из YouTube-видео прямо перед включением
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(BURMALDA_URL, download=False)
                    direct_audio_url = info['url']
                
                # Включаем саму музыку
                vc.play(discord.FFmpegPCMAudio(direct_audio_url, executable=exe_name, before_options=FFMPEG_OPTIONS['before_options'], options=FFMPEG_OPTIONS['options']))
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
