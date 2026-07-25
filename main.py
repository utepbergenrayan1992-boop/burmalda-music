import discord
from discord.ext import tasks
import random
import os

# Считываем переменную, которую ты указал в Values
TOKEN = os.getenv('TOKEN')

# ID текстового канала, куда бот будет писать (замени на свой)
CHANNEL_ID = 1405955231828676755

intents = discord.Intents.default()
intents.members = True 

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен на Railway 24/7!')
    random_ping.start()

# Проверка каждый час. Для теста можно изменить на minutes=1
@tasks.loop(hours=2) 
async def random_ping():
    # 30% шанс срабатывания каждый час для эффекта неожиданности
    if random.random() < 0.5: 
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            # Собираем всех людей на сервере, кроме других ботов
            members = [m for m in channel.guild.members if not m.bot]
            
            if members:
                victim = random.choice(members)
                # Пингуем случайного чела и пишем фразу
                await channel.send(f'{victim.mention} ты бабина')

# Запуск бота через скрытую переменную
bot.run(TOKEN)
