import asyncio
import discord
from redbot.core import commands
import requests
import random
from bs4 import BeautifulSoup

class fyp(commands.Cog):
    """Get trending TikTok videos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fyp(self, ctx):
        """Get the trending TikTok videos"""
        url = "https://www.tiktok.com/en/trending"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        videos = soup.find_all("h2", {"class": "jsx-3852143988"})
        if not videos:
            await ctx.send("Sorry, there are no trending TikTok videos available right now.")
            return
        random_video = random.choice(videos)
        video_title = random_video.text
        video_url = "https://www.tiktok.com" + random_video.parent.get("href")
        # Create the response message
        response = f"Here's a trending TikTok video: {video_title} - {video_url}"
        # Send the response to the Discord channel
        await ctx.send(response)

