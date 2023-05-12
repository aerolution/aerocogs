from .tiktok import fyp


async def setup(bot):
    await bot.add_cog(fyp(bot))

