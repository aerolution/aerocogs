import discord
from discord.ext import commands

class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):
        channel = ctx.channel
        everyone = channel.guild.default_role
        bot_member = channel.guild.me
        overwrite = channel.overwrites_for(everyone)

        if overwrite.send_messages is None or overwrite.send_messages:
            # Channel is not locked, so we need to lock it
            overwrite.send_messages = False
            await channel.set_permissions(everyone, overwrite=overwrite)
            await ctx.send(f"{bot_member.mention} has **locked** the channel {channel.mention}.")

        else:
            # Channel is already locked, so we need to unlock it
            overwrite.send_messages = True
            await channel.set_permissions(everyone, overwrite=overwrite)
            await ctx.send(f"{bot_member.mention} has **unlocked** the channel {channel.mention}.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
