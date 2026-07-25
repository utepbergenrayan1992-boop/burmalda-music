import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530510035321356338

# Сюда вставь ссылку на YouTube видео со своим треком (можно доступ по ссылке)
YOUTUBE_URL = "https://www.youtube.com/watch?v=5h84DVeMom4"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Настройки для прямого стриминга звука с серверов YouTube
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_playlist(vc):
    while vc.is_connected():
        print("Запуск бесконечного стриминга трека из YouTube...", flush=True)
        source = None
        try:
            # Используем yt-dlp, который автоматически вытягивает чистый аудиопоток
            import yt_dlp
            ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(YOUTUBE_URL, download=False)
                stream_url = info['url']
                
            source = discord.FFmpegPCMAudio(
                stream_url, 
                before_options=FFMPEG_OPTIONS['before_options'], 
                options=FFMPEG_OPTIONS['options']
            )
            vc.play(source)
        except Exception as e:
            print(f"Ошибка стриминга: {e}", flush=True)
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
    print(f"Бот {bot.user} успешно запущен через YouTube Stream!", flush=True)
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
