import io
import os
import urllib.request
import discord
from redbot.core import commands
from instagrapi import Client
from instagrapi.types import Post


class Instagram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = Client()

    @commands.command()
    async def ig(self, ctx, username):
        """Displays profile picture, follower count, following count, bio, and the most recent post on an Instagram account."""
        try:
            user_id = await self.client.user_id_from_username(username)
            user_info = await self.client.user_info(user_id)
            profile_pic_url = user_info.profile_pic_url
            follower_count = user_info.follower_count
            following_count = user_info.following_count
            bio = user_info.biography
            posts = await self.client.user_feed(user_id)
            post: Post = posts[0]
            post_url = f"https://www.instagram.com/p/{post.shortcode}/"
            post_image_url = post.image_versions2.candidates[0].url

            # Download the profile picture and post image
            with urllib.request.urlopen(profile_pic_url) as u, open("profile.jpg", "wb") as f:
                f.write(u.read())
            with urllib.request.urlopen(post_image_url) as u, open("post.jpg", "wb") as f:
                f.write(u.read())

            # Send the response message to the Discord channel
            response = f"**{user_info.username}**\n{bio}\n\nFollowers: {follower_count} | Following: {following_count}"
            await ctx.send(response, files=[discord.File("profile.jpg"), discord.File("post.jpg")], content=post_url)

            # Delete the image files after they've been sent
            os.remove("profile.jpg")
            os.remove("post.jpg")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
