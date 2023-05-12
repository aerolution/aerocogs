import discord
from redbot.core import commands
import instaloader

class Instagram(commands.Cog):
    """Instagram command."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ig(self, ctx, username):
        """Get information about an Instagram account."""
        try:
            L = instaloader.Instaloader()
            profile = instaloader.Profile.from_username(L.context, username)

            # Get the profile picture
            profile_pic_url = profile.profile_pic_url
            await ctx.send(profile_pic_url)

            # Get the follower count and following count
            follower_count = profile.followers
            following_count = profile.followees
            await ctx.send(f"Follower count: {follower_count}\nFollowing count: {following_count}")

            # Get the bio
            bio = profile.biography
            await ctx.send(f"Bio: {bio}")

            # Get the most recent post and its link
            post = profile.get_posts()[0]
            post_url = f"https://www.instagram.com/p/{post.shortcode}/"
            await ctx.send(post_url)

        except Exception as e:
            await ctx.send(f"Error: {e}")


