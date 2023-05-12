import os
import asyncio
import discord
from redbot.core import commands
from tiktokapi import TikTokApi

api = TikTokApi.get_instance()

class MyCog(commands.Cog):
    """Get trending TikTok videos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tiktok(self, ctx):
        """Get the trending TikTok videos"""
        trending = api.trending(count=5)
        # Filter the videos with dogs and cats hashtags
        filtered = [video for video in trending if "#dogs" in video['desc'] and "#cats" in video['desc']]
        # Create the response message
        response = ""
        for i, video in enumerate(filtered):
            response += f"{i+1}. {video['desc']} - {video['video']['downloadAddr']}\n"
        # Send the response to the Discord channel
        await ctx.send(response)
