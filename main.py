import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530510035321356338

# Рабочая прямая ссылка на твой трек из Dropbox
TRACKS_URLS = [
    "https://dropbox.com"
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_playlist(vc):
    while vc.is_connected():
        if not TRACKS_URLS:
            await asyncio.sleep(10)
            continue

        for track_url in TRACKS_URLS:
            if not vc.is_connected():
                break

            print("Запуск бесконечного стриминга трека BURMALDA FM из Dropbox...", flush=True)
            source = None
            try:
                source = discord.FFmpegPCMAudio(
                    track_url, 
                    before_options=FFMPEG_OPTIONS['before_options'], 
                    options=FFMPEG_OPTIONS['options']
                )
                vc.play(source)
            except Exception as e:
                print(f"Ошибка при запуске FFmpeg: {e}", flush=True)
                if source:
                    source.cleanup()
                await asyncio.sleep(5)
                continue

            while vc.is_connected() and vc.is_playing():
                await asyncio.sleep(2)
            
            if source:
                try:
                    source.cleanup()
                except Exception:
                    pass
                    
            print("Поток завершен. Перезапуск цикла...", flush=True)
            await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен через Dropbox Stream!", flush=True)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Ошибка входа в канал: {e}", flush=True)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(5)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
                bot.loop.create_task(play_playlist(vc))
            except Exception:
                pass

bot.run(TOKEN)
