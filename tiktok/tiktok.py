import discord
from discord.ext import commands
from tikapi import TikAPI

class fyp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api = TikAPI(api_key="your_api_key_here")

    @commands.command()
    async def popular(self, ctx):
        tiktoks = self.api.popular()

        for tiktok in tiktoks:
            title = tiktok['author']['uniqueId']
            description = tiktok['desc']
            url = tiktok['video']['urls'][0]
            likes = tiktok['stats']['diggCount']
            shares = tiktok['stats']['shareCount']

            embed = discord.Embed(title=title, description=description)
            embed.set_image(url=url)
            embed.set_footer(text=f"Likes: {likes} | Shares: {shares}")

            await ctx.send(embed=embed)

    @commands.command()
    async def trending(self, ctx, limit=10):
        tiktoks = self.api.trending(limit=limit)

        for tiktok in tiktoks:
            title = tiktok['author']['uniqueId']
            description = tiktok['desc']
            url = tiktok['video']['urls'][0]
            likes = tiktok['stats']['diggCount']
            shares = tiktok['stats']['shareCount']

            embed = discord.Embed(title=title, description=description)
            embed.set_image(url=url)
            embed.set_footer(text=f"Likes: {likes} | Shares: {shares}")

            await ctx.send(embed=embed)

    @commands.command()
    async def search(self, ctx, query):
        tiktoks = self.api.search(query)

        for tiktok in tiktoks:
            title = tiktok['author']['uniqueId']
            description = tiktok['desc']
            url = tiktok['video']['urls'][0]
            likes = tiktok['stats']['diggCount']
            shares = tiktok['stats']['shareCount']

            embed = discord.Embed(title=title, description=description)
            embed.set_image(url=url)
            embed.set_footer(text=f"Likes: {likes} | Shares: {shares}")

            await ctx.send(embed=embed)

    @commands.command()
    async def like(self, ctx, tiktok_id):
        self.api.like(tiktok_id)
        await ctx.send(f"Liked TikTok with ID {tiktok_id}")

    @commands.command()
    async def follow(self, ctx, user_id):
        self.api.follow(user_id)
        await ctx.send(f"Followed user with ID {user_id}")

    @commands.command()
    async def unfollow(self, ctx, user_id):
        self.api.unfollow(user_id)
        await ctx.send(f"Unfollowed user with ID {user_id}")

    @commands.command()
    async def get_user(self, ctx, user_id):
        user = self.api.user(unique_id=user_id, account_key="your_account_key_here")

        username = user['uniqueId']
        bio = user['signature']
        avatar = user['avatarThumb']

        following = user['following']
        followers = user['fans']

        embed = discord.Embed(title=username, description=bio)
        embed.set_image(url=avatar)
        embed.set_footer(text=f"Following: {following} | Followers: {followers}")

        await ctx.send(embed=embed)

    @commands.command()
    async def get_tiktok(self, ctx, tiktok_id):
        tiktok = self.api.get_tiktok(tiktok_id)

        title = tiktok['author']['uniqueId']
        description = tiktok['desc']
        url = tiktok['video']['urls'][0]
        likes = tiktok['stats']['diggCount']
        shares = tiktok['stats']['shareCount']

        embed = discord.Embed(title=title, description=description)
        embed.set_image(url=url)
        embed.set_footer(text=f"Likes: {likes} | Shares: {shares}")

        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if not reaction.message.embeds:
            return

        if reaction.emoji == "👍":
            await self.api.like(reaction.message.id)
        elif reaction.emoji == "👎":
            await self.api.dislike(reaction.message.id)
