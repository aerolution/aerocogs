from .imglock import ImgLock


async def setup(bot):
    await bot.add_cog(ImgLock(bot))
