import discord
from discord.ext import commands, tasks
import random
import os

# Считываем токен из переменной TOKEN на Railway
TOKEN = os.getenv('TOKEN')

# ID текстового канала, куда бот будет сам писать по таймеру (вставь свой ID)
CHANNEL_ID = 1405955231828676755  

# Имя файла твоей картинки, который лежит в папке с ботом
IMAGE_FILE_NAME = "buster.png" 

intents = discord.Intents.default()
intents.members = True          # Чтобы видеть список людей
intents.message_content = True  # Чтобы читать команды

bot = commands.Bot(command_prefix="!", intents=intents)

async def send_babina(channel):
    """Функция ищет случайного чела и пишет строго фразу 'ты баба'"""
    human_members = []
    async for member in channel.guild.fetch_members(limit=None):
        if not member.bot:
            human_members.append(member)
            
    if human_members:
        victim = random.choice(human_members)
        await channel.send(f'{victim.mention} ты баба')

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен! Картинка загружается локально.')
    if not random_ping.is_running():
        random_ping.start()

# 1. КОМАНДА: пишем в чат «!кто баба»
@bot.command(name="кто")
async def manual_babina(ctx, *, arg=None):
    if arg and arg.lower().strip() == "баба":
        await send_babina(ctx.channel)

# 2. КОМАНДА: пишем в чат «!бустер»
@bot.command(name="бустер")
async def manual_buster(ctx):
    # Проверяем, существует ли файл в папке
    if os.path.exists(IMAGE_FILE_NAME):
        # Отправляем картинку реальным файлом с хостинга
        await ctx.channel.send(file=discord.File(IMAGE_FILE_NAME))
    else:
        await ctx.channel.send("Ошибка: файл картинки не найден в папке бота!")

# 3. РАБОТА ПО ТАЙМЕРУ: проверка каждый час с шансом 30%
@tasks.loop(hours=1)
async def random_ping():
    if random.random() < 0.3:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            # 50% шанс, что отправится пинг "ты баба", и 50% шанс, что отправится твоя картинка
            if random.choice([True, False]):
                await send_babina(channel)
            else:
                if os.path.exists(IMAGE_FILE_NAME):
                    await channel.send(file=discord.File(IMAGE_FILE_NAME))

bot.run(TOKEN)
