from .image_search import ImageSearch

async def setup(bot):
    await bot.add_cog(ImageSearch(bot))
