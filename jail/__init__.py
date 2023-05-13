from .jail import JailCog

await def setup(bot):
    bot.add_cog(JailCog(bot))
