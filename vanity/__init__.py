from .vanity import VanityChecker

async def setup(bot):
    await bot.add_cog(VanityChecker(bot))
