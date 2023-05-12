import discord
from redbot.core import commands
import random
import requests
import os
from bs4 import BeautifulSoup

class fyp(commands.Cog):
    """Get trending TikTok videos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fyp(self, ctx):
        """Download and send a random TikTok video"""
        url = "https://www.tiktok.com/en/trending"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        videos = soup.find_all("h2", {"class": "jsx-3852143988"})
        
        if not videos:
            response = "Sorry, but there are no trending videos available right now"
            await ctx.send(response)
            return
        
        random_video = random.choice(videos)
        video_url = "https://www.tiktok.com" + random_video.parent.get("href")
        video_id = video_url.split("/")[-1]
        api_url = f"https://www.tiktok.com/node/share/video/{video_id}"
        
        response = requests.get(api_url)
        if response.status_code != 200:
            response = "Sorry, but there was an error downloading the video"
            await ctx.send(response)
            return
        
        data = response.json()
        video_url = data["itemInfo"]["itemStruct"]["video"]["playAddr"]
        
        response = requests.get(video_url, stream=True)
        with open('video.mp4', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        with open('video.mp4', 'rb') as f:
            file = discord.File(f, filename='video.mp4')
            caption = data["itemInfo"]["itemStruct"]["desc"]
            publisher = data["itemInfo"]["itemStruct"]["author"]["nickname"]
            response = f"{caption}\n\nPublisher: {publisher}"
            await ctx.send(response, file=file)
        
        os.remove('video.mp4')


