import discord
from redbot.core import commands
from tiktokapipy.async_api import AsyncTikTokAPI
import aiohttp
import io


class TikTok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = AsyncTikTokAPI()

    @commands.command()
    async def trending(self, ctx):
        challenge_name = "fyp"
        count = self.api.challenge.video_limit
        challenge_data = await self.api.challenge(challenge_name, count=1)
        video = challenge_data['items'][0]

        async with aiohttp.ClientSession() as session:
            async with session.get(video['video']['download_addr']) as resp:
                video_data = await resp.read()

        video_file = discord.File(io.BytesIO(video_data), filename="trending_tiktok.mp4")

        embed = discord.Embed(title=video['desc'], color=discord.Color.blue())
        embed.set_author(name=f"@{video['author']['unique_id']}", icon_url=video['author']['avatar_thumb'])
        embed.set_footer(text=f"Uploaded on {video['create_time']}")

        await ctx.send(file=video_file, embed=embed)
