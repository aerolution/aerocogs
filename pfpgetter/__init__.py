from .pfp import ProfileHelper

async def setup(bot):
    await bot.add_cog(ProfileHelper(bot))
