from .roblox import Roblox

async def setup(bot):
  await bot.add_cog(Roblox(bot))
