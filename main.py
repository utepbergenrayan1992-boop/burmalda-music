import sys
import os
import asyncio
import re
import discord
from discord.ext import commands
import aiohttp

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530510035321356338
FILE_ID = "1jIigUWHVnz0bubHF0Bg5MiO7h7l22I_A"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def get_google_drive_stream_url(file_id):
    base_url = "https://google.com"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}&id={file_id}") as response:
            html = await response.text()
            match = re.search(r'confirm=([0-9a-zA-Z_]+)', html)
            if match:
                confirm_token = match.group(1)
                return f"{base_url}&confirm={confirm_token}&id={file_id}"
            return f"{base_url}&id={file_id}"

async def play_playlist(vc):
    while vc.is_connected():
        if not vc.is_connected():
            break

        print("Получаем рабочий поток с Google Диска...", flush=True)
        try:
            track_url = await get_google_drive_stream_url(FILE_ID)
        except Exception as e:
            print(f"Не удалось обойти защиту Google: {e}", flush=True)
            await asyncio.sleep(10)
            continue

        print("Запуск бесконечного стриминга трека BURMALDA FM...", flush=True)
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
    print(f"Бот {bot.user} успешно запущен через Google Drive Bypass!", flush=True)
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
