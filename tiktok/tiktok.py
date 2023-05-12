import asyncio
import discord
from redbot.core import commands
import requests
from bs4 import BeautifulSoup

class MyCog(commands.Cog):
    """Get trending TikTok videos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tiktok(self, ctx):
        """Get the trending TikTok videos"""
        url = "https://www.tiktok.com/en/trending"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        videos = soup.find_all("h2", {"class": "jsx-3852143988"})
        random_video = videos[random.randint(0, len(videos)-1)]
        video_title = random_video.text
        video_url = "https://www.tiktok.com" + random_video.parent.get("href")
        # Create the response message
        response = f"Here's a trending TikTok video: {video_title} - {video_url}"
        # Send the response to the Discord channel
        await ctx.send(response)
