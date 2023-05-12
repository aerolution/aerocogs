from .tiktok import ftp


async def setup(bot):
    await bot.add_cog(fyp(bot))

