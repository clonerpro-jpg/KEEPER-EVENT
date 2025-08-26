import disnake
from disnake.ext import commands
import sqlite3

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_data(self, user_id, guild_id):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT coins, xp FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
        data = c.fetchone()
        conn.close()
        return data

    @commands.slash_command(description="Показать профиль пользователя")
    async def profile(self, inter, member: disnake.Member = None):
        member = member or inter.author
        data = self.get_user_data(member.id, inter.guild.id)

        if not data:
            coins, xp = 0, 0
        else:
            coins, xp = data

        embed = disnake.Embed(
            title=f"Профиль {member.display_name}",
            color=disnake.Color.blue()
        )
        embed.add_field(name="User ID", value=member.id, inline=False)
        embed.add_field(name="Guild ID", value=inter.guild.id, inline=False)
        embed.add_field(name="Coins", value=coins, inline=True)
        embed.add_field(name="XP", value=xp, inline=True)
        embed.add_field(
            name="Дата регистрации в Discord",
            value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"),
            inline=False
        )

        if member.joined_at:
            embed.add_field(
                name="Дата входа на сервер",
                value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"),
                inline=False
            )

        await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Profile(bot))