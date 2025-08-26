import disnake
from disnake.ext import commands
from database import get_conn


class XPMultiplier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="setxplvl", description="Настройки множителя опыта (ХП)")
    @commands.has_permissions(administrator=True)
    async def xpmultiplier(self, inter: disnake.ApplicationCommandInteraction,
                           value: float = None):
        """
        /xpmultiplier → показать текущий множитель
        /xpmultiplier <число> → изменить множитель (например 2 = х2)
        """

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT xp_multiplier FROM guilds WHERE guild_id=?", (inter.guild.id,))
        row = cursor.fetchone()

        if value is None:
            if row:
                await inter.response.send_message(
                    f"Текущий множитель опыта на сервере: **x{row[0]}**", ephemeral=True
                )
            else:
                await inter.response.send_message(
                    "На сервере ещё не установлен множитель (по умолчанию x1)"
                )
        else:
            if row:
                cursor.execute("UPDATE guilds SET xp_multiplier=? WHERE guild_id=?",
                               (value, inter.guild.id))
            else:
                cursor.execute("INSERT INTO guilds (guild_id, xp_multiplier) VALUES (?, ?)",
                               (inter.guild.id, value))
            conn.commit()

            await inter.response.send_message(
                f"Множитель опыта обновлён: **x{value}**", ephemeral=True
            )

        conn.close()


def setup(bot):
    bot.add_cog(XPMultiplier(bot))