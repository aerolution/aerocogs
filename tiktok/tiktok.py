import discord
from redbot.core import commands
from tikapi import TikAPI

class TikTok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok_api = TikAPI("YOUR_API_KEY")

    @commands.command()
    async def tiktok(self, ctx, username):
        """Fetches a user's latest TikTok video."""
        try:
            user_videos = self.tiktok_api.getUser(username)
            latest_video = user_videos[0]
            video_url = latest_video['video']['downloadAddr']
            await ctx.send(f"Latest TikTok video from {username}: {video_url}")
        except Exception as e:
            await ctx.send(f"Error fetching TikTok video: {e}")
