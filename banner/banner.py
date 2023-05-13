import discord
from discord.ext import commands
from redbot.core import Config, checks, commands

class Banner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def showbanner(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_banner_url = await self.get_user_banner_url(member)
        server_banner_url = await self.get_server_banner_url(ctx.guild)

        if user_banner_url is None:
            await ctx.send("This user does not have a banner.")
            return

        embed = discord.Embed(title=f"{member.name}'s Banner")
        embed.set_image(url=user_banner_url)
        message = await ctx.send(embed=embed)

        if user_banner_url != server_banner_url:
            await message.add_reaction("➡️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "➡️"

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reaction("➡️")
            else:
                embed.set_image(url=server_banner_url)
                await message.edit(embed=embed)
                await message.clear_reaction("➡️")

    async def get_user_banner_url(self, member: discord.Member):
        if member.is_avatar_animated():
            return member.avatar_url_as(format="gif")
        else:
            return member.avatar_url_as(format="png")

    async def get_server_banner_url(self, guild: discord.Guild):
        if guild.banner:
            return guild.banner_url_as(format="png")
        else:
            return None

def setup(bot):
    bot.add_cog(Banner(bot))
