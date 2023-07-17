from .imgsnipe import ImgSnipe

async def setup(bot):
    await bot.add_cog(ImgSnipe(bot))
