import disnake
from disnake.ext import commands
from database import get_conn


class AddItem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="additem", description="Добавить товар в магазин")
    @commands.has_permissions(administrator=True)
    async def additem(self, inter: disnake.ApplicationCommandInteraction,
                      name: str,
                      price: int,
                      type: str = commands.Param(choices=["role", "item"]),
                      role: disnake.Role = None):
        """
        Добавить предмет в магазин.
        - name: название
        - price: цена
        - type: role/item
        - role: если type=role, то нужно указать роль
        """

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO shop_items (name, price, type, role_id)
        VALUES (?, ?, ?, ?)
        """, (name, price, type, role.id if role else None))

        conn.commit()
        conn.close()

        await inter.response.send_message(
            f"Товар добавлен в магазин:\n"
            f"**Название:** {name}\n"
            f"**Цена:** {price}\n"
            f"**Тип:** {type}\n"
            f"{f'**Роль:** {role.mention}' if role else ''}", ephemeral=True
        )


def setup(bot):
    bot.add_cog(AddItem(bot))