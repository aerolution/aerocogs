import os
import asyncio
import discord
from redbot.core import commands
from tiktokpy import TikTokPy

api = TikTokPy({
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br',
  'Upgrade-Insecure-Requests': '1'
})

class MyCog(commands.Cog):
    """ A custom cog to get trending TikTok videos """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tiktok(self, ctx):
        """ Get the trending TikTok videos """
        print('Executing tiktok command...')
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
