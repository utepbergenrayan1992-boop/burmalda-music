import discord
from discord.ext import commands, tasks
import random
import os

# Считываем токен из переменной TOKEN на Railway
TOKEN = os.getenv('TOKEN')

# ID текстового канала, куда бот будет сам писать по таймеру (вставь свой ID)
CHANNEL_ID = 1405955231828676755  

intents = discord.Intents.default()
intents.members = True          # Чтобы видеть список людей
intents.message_content = True  # Чтобы читать команду !кто баба

bot = commands.Bot(command_prefix="!", intents=intents)

async def send_babina(channel):
    """Единая функция: ищет случайного чела и пишет строго одну фразу"""
    human_members = []
    async for member in channel.guild.fetch_members(limit=None):
        if not member.bot:
            human_members.append(member)
            
    if human_members:
        victim = random.choice(human_members)
        # В чате будет ТУПО это сообщение и больше ничего
        await channel.send(f'{victim.mention} ты баба')

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен! Работает таймер и команда.')
    if not random_ping.is_running():
        random_ping.start()

# 1. РАБОТА ПО КОМАНДЕ: пишем в чат «!кто баба»
@bot.command(name="кто")
async def manual_babina(ctx, *, arg=None):
    if arg and arg.lower().strip() == "баба":
        await send_babina(ctx.channel)

# 2. РАБОТА ПО ТАЙМЕРУ: проверка каждый час с шансом 30%
@tasks.loop(hours=1)
async def random_ping():
    if random.random() < 0.3:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await send_babina(channel)

bot.run(TOKEN)
