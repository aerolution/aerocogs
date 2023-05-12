from redbot.core import commands

class fyp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fyp(self, ctx):
        await ctx.send("This is a test message.")

def setup(bot):









