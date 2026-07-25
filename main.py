import discord
from discord.ext import commands
import asyncio
import os
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1041431136687112196  # ID твоего голосового канала
BURMALDA_URL = "https://youtube.com"  # Ссылка на Бурмалда фм

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

async def keep_playing(vc):
    """Бесконечно удерживает поток активным из YouTube"""
    while vc.is_connected():
        if not vc.is_playing():
            try:
                # Достаем прямую аудиоссылку из YouTube-видео прямо перед включением
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(BURMALDA_URL, download=False)
                    direct_audio_url = info['url']

                # Включаем музыку (без указания executable, Linux найдет его в системе сам)
                source = discord.FFmpegPCMAudio(
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
    # Если бота кикнули из канала, он зайдет обратно через 5 секунд
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
