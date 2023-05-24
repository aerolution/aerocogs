import discord
from redbot.core import commands, Config
import asyncio
import re
from datetime import timedelta

class Jail(commands.Cog):
    """
    Put users in a jail! (Channel.)
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"jail_channel": None, "jail_log_channel": None}
        self.config.register_guild(**default_guild)

    async def notify_log_channel(self, guild, embed):
        log_channel_id = await self.config.guild(guild).jail_log_channel()
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)

    async def notify_user(self, member, embed):
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            jail_channel_id = await self.config.guild(member.guild).jail_channel()
            jail_channel = member.guild.get_channel(jail_channel_id)
            if jail_channel:
                await jail_channel.send(embed=embed)

    def parse_time(self, time_str):
        time_regex = r"(\d+)([smhd])"  # seconds, minutes, hours, days
        matches = re.findall(time_regex, time_str)
        if matches:
            total_seconds = 0
            for value, unit in matches:
                if unit == "s":
                    total_seconds += int(value)
                elif unit == "m":
                    total_seconds += int(value) * 60
                elif unit == "h":
                    total_seconds += int(value) * 3600
                elif unit == "d":
                    total_seconds += int(value) * 86400
            return total_seconds
        return None

    def format_timedelta(self, seconds):
        delta = timedelta(seconds=seconds)
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_parts = []
        if days:
            time_parts.append(f"{days}d")
        if hours:
            time_parts.append(f"{hours}h")
        if minutes:
            time_parts.append(f"{minutes}m")
        if seconds:
            time_parts.append(f"{seconds}s")
        return " ".join(time_parts)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.group()
    async def jailset(self, ctx):
        """Jail settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @jailset.command(name="channel")
    async def jailset_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel to use as the jail."""
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        await ctx.send(f"The jail channel has been set to {channel.mention}.")

    @jailset.command(name="logs")
    async def jailset_logs(self, ctx, channel: discord.TextChannel):
        """Set the channel to use for jail logs."""
        await self.config.guild(ctx.guild).jail_log_channel.set(channel.id)
        await ctx.send(f"The jail log channel has been set to {channel.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member: discord.Member, *args):
        """Jail a user and restrict them to a single specified channel.
        
        You can optionally specify a jail time after the reason. Examples:
        !jail @user being bad for 1h
        !jail @user spamming for 30m
        """

        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        # Get author
        author = ctx.author

        # Get all channels in the guild
        channels = ctx.guild.channels

        # Deny send messages and view channel permissions in all channels
        for channel in channels:
            await channel.set_permissions(member, send_messages=False, view_channel=False)

        # Allow send messages permission only in the jail channel
        await jail_channel.set_permissions(member, send_messages=True, view_channel=True)

        # Parse the jail time and reason if provided
        reason = " ".join(args)
        jail_time = self.parse_time(reason)
        formatted_reason = reason

        if jail_time:
            formatted_reason = formatted_reason.rsplit(None, 1)[0]  # Remove the time from the reason
            formatted_time = self.format_timedelta(jail_time)
            formatted_reason += f" (Jail time: {formatted_time})"

        # Create an embed message
        embed = discord.Embed(title="User was Jailed!", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Moderator", value=author.mention, inline=False)
        embed.add_field(name="Jailed at", value=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        if formatted_reason:
            embed.add_field(name="Reason", value=formatted_reason, inline=False)
        if jail_time:
            embed.add_field(name="Jail time", value=formatted_time, inline=False)
        embed.set_thumbnail(url=author.avatar_url)

        await ctx.send(embed=embed)

        # Send the embed message to the user or jail channel
        await self.notify_user(member, embed)

        # Notify the jail log channel
        await self.notify_log_channel(ctx.guild, embed)

        if jail_time:
            await asyncio.sleep(jail_time)
            await self.unjail(ctx, member, reason="User served their time.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unjail(self, ctx, member: discord.Member, *, reason: str = None):
        """Unjail a user and restore their permissions."""
        # Get all channels in the guild
        channels = ctx.guild.channels

        # Remove permission overwrites for the member in all channels
        for channel in channels:
            await channel.set_permissions(member, overwrite=None)

        # Create an embed message
        embed = discord.Embed(title="User was Unjailed!", color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.add_field(name="Unjailed at", value=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

        # Send the embed message to the user or jail channel
        await self.notify_user(member, embed)

        # Notify the jail log channel
        await self.notify_log_channel(ctx.guild, embed)
