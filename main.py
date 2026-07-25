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

# Настройки FFmpeg для стабильного интернет-потока
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

            print(f"Запуск стриминга трека BURMALDA FM (по кругу)...", flush=True)
            
            source = None
            try:
                source = discord.FFmpegPCMAudio(
                    track_url, 
                    before_options=FFMPEG_OPTIONS['before_options'], 
                    options=FFMPEG_OPTIONS['options']
                )
                vc.play(source)
            except Exception as e:
                print(f"Ошибка при запуске потока: {e}")
                if source:
                    source.cleanup()
                await asyncio.sleep(5)
                continue

            # Ждем завершения трека, но СТРОГО проверяем, что бот всё еще в войсе
            while vc.is_connected() and vc.is_playing():
                await asyncio.sleep(2)
            
            if source:
                try:
                    source.cleanup()
                except Exception:
                    pass
                    
            print("Круг завершен или соединение разорвано. Перезапуск...", flush=True)
            await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен!")
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Если бот вылетел из-за ошибки 4017, этот кусок переподключит его обратно
    if member.id == bot.user.id and after.channel is None:
        print("Бота выкинуло из канала. Попытка переподключения через 5 секунд...")
        await asyncio.sleep(5)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
                bot.loop.create_task(play_playlist(vc))
            except Exception as e:
                print(f"Ошибка авто-переподключения: {e}")

bot.run(TOKEN)
