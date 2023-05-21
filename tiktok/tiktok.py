from redbot.core import commands

class TikTok(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mycom(self, ctx):
        """Tiktok!"""
        # Your code will go here
        await ctx.send("I can do stuff!")


# def do_something():
  #  with TikTokAPI() as api:
      #  user = api.user(username)
       # for video in user.videos:
        #    num_comments = video.stats.comment_count
        #    num_likes = video.stats.digg_count
      #      num_views = video.stats.play_count
          #  num_shares = video.stats.share_count
