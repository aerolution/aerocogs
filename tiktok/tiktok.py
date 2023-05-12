import discord
from redbot.core import commands
from tikapi import TikAPI

class fyp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok_api = TikAPI("hnxoYBFNO7uQFUpmRkiPNmb3Rr11YJYerx7clmfc7mHRpPWS")

    @commands.command()
    async def fyp(self, ctx, username):
        """Fetches a user's latest TikTok video."""
        try:
            user_videos = self.tiktok_api.getUser(username)
            latest_video = user_videos[0]
            video_url = latest_video['video']['downloadAddr']
            await ctx.send(f"Latest TikTok video from {username}: {video_url}")
        except Exception as e:
            await ctx.send(f"Error fetching TikTok video: {e}")
