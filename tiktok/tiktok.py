import asyncio
import discord
from redbot.core import commands
from TikTokApi import TikTokApi
import random
import aiohttp

class fyp(commands.Cog):
    """Get a random TikTok video from FYP"""

    def __init__(self, bot):
        self.bot = bot
        self.api = TikTokApi()

    @commands.command()
    async def fyp(self, ctx):
        """Get a random TikTok video from FYP"""
        # Get a random TikTok video from FYP
        video = self.api.getTikTokById(self.api.trending(count=100)[random.randint(0,99)]['id'])
        video_url = video['video']['urls'][0]
        caption = video['desc']
        uploader = video['author']['uniqueId']

        # Create the response message
        response = f"Here's a trending TikTok video: {caption} - Uploaded by {uploader}"
        
        # Download the video and send it to the Discord channel
        async with self.bot.session.get(video_url) as r:
            if r.status == 200:
                fp = await ctx.bot.loop.run_in_executor(None, open, f"{random.randint(1,999999)}.mp4", "wb")
                fp.write(await r.read())
                fp.close()
                await ctx.send(response, file=discord.File(f"{random.randint(1,999999)}.mp4"))

        # Delete the video file after it's been sent
        await asyncio.sleep(1)
        await ctx.bot.loop.run_in_executor(None, os.remove, f"{random.randint(1,999999)}.mp4")



