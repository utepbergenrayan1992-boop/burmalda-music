import discord
from discord.ext import commands
import asyncio
import os

# === НАСТРОЙКИ БОТА ===
TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1041431136687112196 
# Ссылка на поток радио Бурмалда FM
BURMALDA_URL = "https://www.youtube.com/watch?v=5h84DVeMom4"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def keep_playing(vc):
    """Бесконечно удерживает поток активным без сообщений в чат"""
    while vc.is_connected():
        if not vc.is_playing():
            try:
                # Автовыбор утилиты: для ПК — ffmpeg.exe, для сервера хостинга — ffmpeg
                executable = 'ffmpeg' if os.name != 'nt' else 'ffmpeg.exe'
                vc.play(discord.FFmpegPCMAudio(BURMALDA_URL, executable=executable, before_options=FFMPEG_OPTIONS['before_options'], options=FFMPEG_OPTIONS['options']))
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен 24/7 без текста в чате!")
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect()
            bot.loop.create_task(keep_playing(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Если бота выкинули из войса, он молча возвращается назад
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
