import disnake
from disnake.ext import commands
import sqlite3

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def register_user(self, user_id, guild_id):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, guild_id) VALUES (?, ?)", (user_id, guild_id))
        conn.commit()
        conn.close()

    def is_channel_allowed(self, guild_id, channel_id):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT 1 FROM xp_channels WHERE guild_id=? AND channel_id=?", (guild_id, channel_id))
        result = c.fetchone()
        conn.close()
        return result is not None

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        guild_id = message.guild.id
        channel_id = message.channel.id

        if not self.is_channel_allowed(guild_id, channel_id):
            return 

        self.register_user(message.author.id, guild_id)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("UPDATE users SET xp = xp + 10 WHERE user_id=? AND guild_id=?",
                  (message.author.id, guild_id))
        conn.commit()
        conn.close()

    @commands.slash_command(description="Включить начисление XP в этом канале")
    @commands.has_permissions(administrator=True)
    async def enable_xp(self, inter):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO xp_channels (guild_id, channel_id) VALUES (?, ?)",
                  (inter.guild.id, inter.channel.id))
        conn.commit()
        conn.close()
        await inter.response.send_message(f"В этом канале теперь начисляется XP!")

    @commands.slash_command(description="Выключить начисление XP в этом канале")
    @commands.has_permissions(administrator=True)
    async def disable_xp(self, inter):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("DELETE FROM xp_channels WHERE guild_id=? AND channel_id=?",
                  (inter.guild.id, inter.channel.id))
        conn.commit()
        conn.close()
        await inter.response.send_message(f"В этом канале XP больше не начисляется.")

def setup(bot):
    bot.add_cog(XP(bot))