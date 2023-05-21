import discord
from redbot.core import commands
from robloxapi import Client

class Roblox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = Client()

    @commands.command()
    async def robloxuser(self, ctx, username: str):
        try:
            user = await self.client.get_user_by_username(username)
        except Exception as e:
            await ctx.send(f"Error: {e}")
            return

        bio = user.description
        followers_count = user.followers_count
        following_count = user.followings_count
        last_online = user.last_online
        avatar_url = user.avatar_url

        embed = discord.Embed(title=f"{username}'s Roblox Info", color=discord.Color.blue())
        embed.add_field(name="Bio", value=bio, inline=False)
        embed.add_field(name="Followers", value=followers_count, inline=True)
        embed.add_field(name="Following", value=following_count, inline=True)
        embed.add_field(name="Last Online", value=last_online, inline=False)
        embed.footer(text="Command invoked by {}".format(ctx.message.author.name))
        embed.set_thumbnail(url=avatar_url)

        await ctx.send(embed=embed)
