import discord
from redbot.core import commands, Config
import asyncio
import re
from datetime import timedelta, datetime
from discord.ui import Button, View

class ImgSnipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2384729834)
        default_guild = {
            "sniped_message": None
        }
        self.config.register_guild(**default_guild)

    async def on_message_delete(self, message):
        if message.attachments:
            await self.config.guild(message.guild).sniped_message.set({
                "content": message.content,
                "author_name": message.author.name,
                "author_avatar": str(message.author.avatar_url),
                "attachment_url": str(message.attachments[0].url)
            })
            

    async def imgsnipe(self, ctx):
        sniped_message = await self.config.guild(ctx.guild).sniped_message()
        if not sniped_message:
            return await ctx.send("No recently deleted message with an image found.")
        
        embed = discord.Embed(title=f"Sniped by: {ctx.author}", color=0xFF5733)
        embed.add_field(name="Content", value=sniped_message["content"], inline=False)
        embed.set_footer(text=f"Deleted by: {sniped_message['author_name']}", icon_url=sniped_message['author_avatar'])
        embed.set_image(url=sniped_message["attachment_url"])
        await ctx.send(embed=embed)
