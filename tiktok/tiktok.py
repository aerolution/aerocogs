# written by chatgpt LOL     bot.add_cog(fyp(bot))
import os
import tempfile
import aiohttp
import discord
from redbot.core import commands
from TikTokApi import TikTokApi

class fyp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = TikTokApi()

    @commands.command()
    async def fyp(self, ctx):
        # Fetch trending TikTok videos
        trending_videos = self.api.trending(count=1)

        # Download and send the first video
        video = trending_videos[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(video['video']['downloadAddr']) as resp:
                video_data = await resp.read()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(video_data)
            temp_file.flush()
            temp_file.seek(0)

            # Create an embed with video details
            embed = discord.Embed(title=video['desc'], color=0x00ff00)
            embed.set_author(name=video['author']['uniqueId'])
            embed.set_footer(text=f"Uploaded on {video['createTime']}")

            # Send the video and embed to the chat
            await ctx.send(file=discord.File(temp_file.name, f"{video['id']}.mp4"), embed=embed)

            # Clean up the temporary file
            os.unlink(temp_file.name)

def setup(bot):
    bot.add_cog(fyp(bot))






