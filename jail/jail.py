import discord
from redbot.core import commands, Config


class Jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"jail_channel": None, "jail_log_channel": None}
        self.config.register_guild(**default_guild)

    async def notify_log_channel(self, guild, message):
        log_channel_id = await self.config.guild(guild).jail_log_channel()
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(message)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member: discord.Member, *, reason: str):
        """Jail a user and restrict them to a single specified channel."""
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        if not jail_channel_id:
            await ctx.send("Jail channel not set. Please set it using `setjailchannel` command.")
            return

        jail_channel = ctx.guild.get_channel(jail_channel_id)
        if not jail_channel:
            await ctx.send("Jail channel not found. Please set a valid channel using `setjailchannel` command.")
            return

        default_role = ctx.guild.default_role
        default_role_overwrite = jail_channel.overwrites_for(default_role)
        default_role_overwrite.send_messages = False

        member_overwrite = jail_channel.overwrites_for(member)
        member_overwrite.send_messages = True

        await jail_channel.set_permissions(default_role, overwrite=default_role_overwrite, reason=reason)
        await jail_channel.set_permissions(member, overwrite=member_overwrite, reason=reason)

        # Create an embed message
        embed = discord.Embed(title="User Jailed", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Jailed by {ctx.author}", icon_url=ctx.message.author.avatar)

        # Send the embed message to the context channel
        await ctx.send(embed=embed)

        # Notify the jail log channel
        await self.notify_log_channel(ctx.guild, f"{member.mention} has been jailed for {reason} by {ctx.author.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unjail(self, ctx, member: discord.Member, *, reason: str):
        """Unjail a user and restore their permissions."""
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        if not jail_channel_id:
            await ctx.send("Jail channel not set. Please set it using `setjailchannel` command.")
            return

        jail_channel = ctx.guild.get_channel(jail_channel_id)
        if not jail_channel:
            await ctx.send("Jail channel not found. Please set a valid channel using `setjailchannel` command.")
            return

        await jail_channel.set_permissions(member, overwrite=None, reason=reason)
        
        # message author
        author = ctx.message.author
        
        # Create an embed message
        embed = discord.Embed(title="User Unjailed", color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Unjailed by {author}", icon_url=author.avatar)

        # Send the embed message to the context channel
        await ctx.send(embed=embed)

        # Notify the jail log channel
        await self.notify_log_channel(ctx.guild, f"{member.mention} has been unjailed for {reason} by {ctx.author.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def setjailchannel(self, ctx, channel: discord.TextChannel):
        """Set the jail channel for this server."""
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        await ctx.send(f"Jail channel has been set to {channel.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def setjaillogchannel(self, ctx, channel: discord.TextChannel):
        """Set the jail log channel for this server."""
        await self.config.guild(ctx.guild).jail_log_channel.set(channel.id)
        await ctx.send(f"Jail log channel has been set to {channel.mention}.")
