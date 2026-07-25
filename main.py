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
MUSIC_FOLDER = "playlist"  # Название папки с твоими треками .mp3

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Настройки плеера для локальных файлов (без таймаутов интернета)
FFMPEG_OPTIONS = {'options': '-vn'}

async def play_playlist(vc):
    while vc.is_connected():
        # Проверяем, есть ли вообще файлы mp3 в нашей папке
        if not os.path.exists(MUSIC_FOLDER):
            print(f"Ошибка: Создай папку {MUSIC_FOLDER} на GitHub и закинь треки!")
            await asyncio.sleep(10)
            continue
            
        tracks = [os.path.join(MUSIC_FOLDER, f) for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
        
        if not tracks:
            print("В папке playlist нет ни одного .mp3 файла!")
            await asyncio.sleep(10)
            continue

        # Бежим по очереди по каждому треку в нашей папке
        for track_path in tracks:
            if not vc.is_connected():
                break
                
            print(f"Сейчас играет трек: {track_path}", flush=True)
            
            # Запускаем локальный файл
            source = discord.FFmpegPCMAudio(track_path, options=FFMPEG_OPTIONS['options'])
            vc.play(source)
            
            # Ждем, пока трек доиграет до самого конца
            while vc.is_playing():
                await asyncio.sleep(2)
                
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен 24/7 в режиме локального плейлиста!")
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
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
