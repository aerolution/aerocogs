from redbot.core import commands

class fyp(commands.Cog):
    """Fetch TikTok Videos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fyp(self, ctx):
        """This does stuff!"""
        # Your code will go here
        await ctx.send("I can do stuff!")










