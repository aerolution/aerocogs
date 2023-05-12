from .instagram import ig

async def setup(bot):
    await bot.add_cog(fyp(bot))
