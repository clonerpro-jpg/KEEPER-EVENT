import disnake
from disnake.ext import commands
from database import get_conn


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /shop (NOT WORKING! USE /shop view)
    @commands.slash_command(name="shop", description="Магазин ролей и предметов")
    async def shop(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # /shop view
    @shop.sub_command(name="view", description="Посмотреть товары магазина")
    async def shop_view(self, inter: disnake.ApplicationCommandInteraction):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT item_id, name, price, type, role_id FROM shop_items")
        items = cursor.fetchall()
        conn.close()

        if not items:
            await inter.response.send_message("Магазин пуст.", ephemeral=True)
            return

        embed = disnake.Embed(title="Магазин", color=0x3498db)
        for item_id, name, price, type_, role_id in items:
            role_info = f" (роль: <@&{role_id}>)" if role_id else ""
            embed.add_field(
                name=f"{name} — {price}",
                value=f"ID: {item_id} • Тип: `{type_}`{role_info}",
                inline=False
            )
        await inter.response.send_message(embed=embed, ephemeral=True)

    # /shop buy
    @shop.sub_command(name="buy", description="Купить предмет/роль из магазина")
    async def shop_buy(
        self,
        inter: disnake.ApplicationCommandInteraction,
        item: str = commands.Param(name="товар", autocomplete=True)
    ):
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, price, type, role_id FROM shop_items WHERE name = ?",
            (item,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            await inter.response.send_message("Такого товара нет в магазине.", ephemeral=True)
            return

        name, price, type_, role_id = row

        cursor.execute(
            "SELECT coins FROM users WHERE user_id=? AND guild_id=?",
            (inter.author.id, inter.guild.id),
        )
        u = cursor.fetchone()
        if not u:
            conn.close()
            await inter.response.send_message("Вы не зарегистрированы в системе.", ephemeral=True)
            return

        coins = u[0]
        if coins < price:
            conn.close()
            await inter.response.send_message("Недостаточно монет.", ephemeral=True)
            return

        cursor.execute(
            "UPDATE users SET coins = coins - ? WHERE user_id=? AND guild_id=?",
            (price, inter.author.id, inter.guild.id),
        )
        conn.commit()

        if type_ == "role" and role_id:
            role = inter.guild.get_role(int(role_id))
            if role:
                await inter.author.add_roles(role, reason="Покупка в магазине")
                await inter.response.send_message(
                    f"Куплена роль {role.mention} за {price}", ephemeral=True
                )
            else:
                await inter.response.send_message(
                    "Роль с таким ID не найдена на сервере (монеты уже списаны).", ephemeral=True
                )
        else:
            await inter.response.send_message(f"Покупка: {name} за {price}")

        conn.close()

    # /shop sell 
    @shop.sub_command(name="sell", description="Продать купленную роль (возврат 50%)")
    async def shop_sell(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role_name: str = commands.Param(name="роль", autocomplete=True), ephemeral=True
    ):
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT name, price, role_id FROM shop_items WHERE type='role' AND name=?",
            (role_name,),
        ) 
        row = cursor.fetchone()
        if not row:
            conn.close()
            await inter.response.send_message("Эта роль не продаётся в магазине.", ephemeral=True)
            return

        name, price, role_id = row
        role = inter.guild.get_role(int(role_id)) if role_id else None

        if not role or role not in inter.author.roles:
            conn.close()
            await inter.response.send_message("У тебя нет этой роли.", ephemeral=True)
            return

        await inter.author.remove_roles(role, reason="Продажа роли в магазине")

        refund = price // 2
        cursor.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id=? AND guild_id=?",
            (refund, inter.author.id, inter.guild.id),
        )
        conn.commit()
        conn.close()

        await inter.response.send_message(
            f"Продажа {role.mention}: возвращено {refund}", ephemeral=True
        )

    # autodops

    # autodops for spisok tovarov /shop buy
    @shop_buy.autocomplete("товар")
    async def shop_buy_autocomplete(self, inter: disnake.ApplicationCommandInteraction, string: str):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM shop_items WHERE name LIKE ? ORDER BY name LIMIT 25",
            (f"%{string}%",),
        )
        names = [r[0] for r in cursor.fetchall()]
        conn.close()
        return names

    # autodops 2
    @shop_sell.autocomplete("роль")
    async def shop_sell_autocomplete(self, inter: disnake.ApplicationCommandInteraction, string: str):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, role_id FROM shop_items WHERE type='role' AND role_id IS NOT NULL"
        )
        rows = cursor.fetchall()
        conn.close()

        have_and_sellable = []
        for name, role_id in rows:
            role = inter.guild.get_role(int(role_id))
            if role and role in inter.author.roles and string.lower() in name.lower():
                have_and_sellable.append(name)

        return have_and_sellable[:25]


def setup(bot):
    bot.add_cog(Shop(bot))