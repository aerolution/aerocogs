import discord
import io
import ttapi
import aiohttp
from redbot.core import commands

class TikTokFYP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = ttapi.TikTokAPI()

    @commands.command(name="fyp")
    async def fyp(self, ctx):
        try:
            async with ctx.channel.typing():
                tiktok = self.api.get_trending(count=1)
                video_data = tiktok[0]
                video_url = video_data.video_url
                video_caption = video_data.caption
                video_author = f"{video_data.author.nickname} (@{video_data.author.unique_id})"
                video_stats = f"{video_data.stats.likes:,} 👍 | {video_data.stats.comments:,} 💬 | {video_data.stats.views:,} 👀 ({video_data.stats.shares:,} 🔗)"

                async with aiohttp.ClientSession() as session:
                    async with session.get(video_url) as response:
                        video_bytes = io.BytesIO(await response.read())

                embed = discord.Embed(color=discord.Color.random(), description=f"**[{video_caption}]({video_url})**")
                embed.set_author(name=video_author, icon_url=video_data.author.avatar_url)
