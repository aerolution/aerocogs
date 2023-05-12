import asyncio
import discord
from redbot.core import commands
from TikTokApi import TikTokApi
import random
import aiohttp
import os

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
        




