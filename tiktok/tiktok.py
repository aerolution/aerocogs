import os
import asyncio
import discord
from tiktokpy import TikTokPy
from redbot.core import commands

api = TikTokPy()

class fyp(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def fyp(self, ctx):
      print('Executing trendingvids command...')
      try:
          # Fetch the trending videos from TikTok API
          trending = api.trending(count=5)

          # Filter the videos with #dogs and #cats hashtags
          filtered = [video for video in trending if "#dogs" in video['desc'] and "#cats" in video['desc']]

          # Create the response message
          response = ""
          for i, video in enumerate(filtered):
              response += f"{i+1}. {video['desc']} - {video['video']['urls'][0]}\n"

          print('Sending response...')
          # Send the response to the Discord channel
          await ctx.send(response)
      except Exception as e:
          print('Error:', e)
