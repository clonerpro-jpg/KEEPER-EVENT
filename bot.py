import os
import disnake
from disnake.ext import commands
from database import init_db

intents = disnake.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.InteractionBot(intents=intents)

def load_cogs():
    cogs_dir = "./cogs"
    for filename in os.listdir(cogs_dir):
        if not filename.endswith(".py"):
            continue
        if filename.startswith("_") or filename == "__init__.py":
            continue

        modulename = f"cogs.{filename[:-3]}"
        try:
            bot.load_extension(modulename)
            print(f"Загружен ког: {filename}")
        except Exception as e:
            print(f"Не удалось загрузить {modulename}: {e.__class__.__name__}: {e}")

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен и готов.")

if __name__ == "__main__":
    init_db()
    load_cogs()

    bot.run("token")
