import os
import tempfile
import discord
from redbot.core import commands
from tiktokapipy.api import TikTokAPI

class fyp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with TikTokAPI() as api:

    @commands.command()
    async def fyp(self, ctx):
        # Fetch trending TikTok videos
        trending_videos = self.api.get_trending_videos(count=1)

        # Download and send the first video
        video = trending_videos[0]
        async with self.bot.session.get(video['video_url']) as response:
            video_data = await response.read()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(video_data)
            temp_file.flush()
            temp_file.seek(0)

            # Create an embed with video details
            embed = discord.Embed(title=video['description'], color=0x00ff00)
            embed.set_author(name='@' + video['author']['nickname'], url=f"https://www.tiktok.com/@{video['author']['nickname']}")
            embed.set_footer(text=f"Uploaded on {video['create_time']}")

            # Add like, comment, and share counts to the embed
            embed.add_field(name="Likes", value=video['statistics']['digg_count'], inline=True)
            embed.add_field(name="Comments", value=video['statistics']['comment_count'], inline=True)
            embed.add_field(name="Shares", value=video['statistics']['share_count'], inline=True)

            # Send the video and embed to the chat
            await ctx.send(file=discord.File(temp_file.name, f"{video['id']}.mp4"), embed=embed)

            # Clean up the temporary file
            os.unlink(temp_file.name)








