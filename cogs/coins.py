import disnake
from disnake.ext import commands
from database import get_conn


class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="coins", description="Управление монетами")
    @commands.has_permissions(administrator=True)  
    async def coins(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # /coins add
    @coins.sub_command(description="Добавить монеты пользователю")
    async def add(self, inter: disnake.ApplicationCommandInteraction,
                  member: disnake.Member,
                  amount: int):

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id=? AND guild_id=?",
            (amount, member.id, inter.guild.id)
        )
        if cursor.rowcount == 0:
            await inter.response.send_message("Пользователь не найден в БД.", ephemeral=True)
        else:
            conn.commit()
            await inter.response.send_message(
                f"{amount} монет добавлено пользователю {member.mention}.", ephemeral=True
            )
        conn.close()

    # /coins remove
    @coins.sub_command(description="Забрать монеты у пользователя")
    async def remove(self, inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member,
                     amount: int):

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET coins = MAX(coins - ?, 0) WHERE user_id=? AND guild_id=?",
            (amount, member.id, inter.guild.id)
        )
        if cursor.rowcount == 0:
            await inter.response.send_message("Пользователь не найден в БД.", ephemeral=True)
        else:
            conn.commit()
            await inter.response.send_message(
                f"У пользователя {member.mention} отнято {amount} монет.", ephemeral=True
            )
        conn.close()


def setup(bot):
    bot.add_cog(Coins(bot))