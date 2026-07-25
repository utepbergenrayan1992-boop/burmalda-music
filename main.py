import sys
import os
import asyncio

# Костыль-заплатка для Python 3.13 на хостингах
try:
    import audioop
except ModuleNotFoundError:
    import audioop_lts
    sys.modules['audioop'] = audioop_lts

import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530510035321356338

# Стриминг напрямую с твоего Google Диска
TRACKS_URLS = [
    "https://google.com"
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Настройки FFmpeg для стабильного интернет-потока без заиканий
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_playlist(vc):
    while vc.is_connected():
        if not TRACKS_URLS:
            print("Ошибка: Список TRACKS_URLS пуст!")
            await asyncio.sleep(10)
            continue

        for track_url in TRACKS_URLS:
            if not vc.is_connected():
                break

            print(f"Запуск стриминга трека BURMALDA FM...", flush=True)
            
            try:
                source = discord.FFmpegPCMAudio(
                    track_url, 
                    before_options=FFMPEG_OPTIONS['before_options'], 
                    options=FFMPEG_OPTIONS['options']
                )
                vc.play(source)
            except Exception as e:
                print(f"Ошибка при запуске потока: {e}")
                await asyncio.sleep(5)
                continue

            # Ждем завершения трека
            while vc.is_playing():
                await asyncio.sleep(2)
            
            await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен в режиме стриминга с Google Drive!")
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Если бота выкинули из канала, он ждет 10 секунд и заходит обратно
    if member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(10)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
                bot.loop.create_task(play_playlist(vc))
            except Exception:
                pass

bot.run(TOKEN)
