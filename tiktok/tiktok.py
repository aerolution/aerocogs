import os
import asyncio
import discord
from tiktokpy import TikTokPy
from redbot.core import commands

api = TikTokPy(headers={
  'accept': 'application/json, text/plain, */*',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
  'referer': 'https://www.tiktok.com/',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin'
})

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
