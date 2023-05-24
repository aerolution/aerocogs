import discord
from redbot.core import commands, Config
import asyncio
import re
from datetime import timedelta
from discord.ui import Button, View

class ConfirmView(View):
    def __init__(self, timeout, member):
        super().__init__(timeout=timeout)
        self.member = member
        self.value = None

    async def interaction_check(self, interaction: discord.interaction) -> bool:
        return interaction.user == self.member

    async def on_timeout(self):
        if not self.value:
            self.value = False

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, button: Button, interaction: discord.interaction):
        await interaction.response.send_message("Confirmed", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def cancel(self, button: Button, interaction: discord.interaction):
        await interaction.response.send_message("Cancelled", ephemeral=True)
        self.value = False
        self.stop()

async def send_confirmation(ctx, embed):
    view = ConfirmView(timeout=30, member=ctx.author)
    await ctx.send(embed=embed, view=view)
    await view.wait()
    return view.value

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
        pass

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
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        author = ctx.author
        channels = ctx.guild.channels

        for channel in channels:
            await channel.set_permissions(member, send_messages=False, view_channel=False)

        await jail_channel.set_permissions(member, send_messages=True, view_channel=True)

        reason =" ".join(args)
        embed = discord.Embed(
            title="You have been jailed!",
            description=f"Reason: {reason}",
            color=discord.Color.red(),
        )
        confirmation_embed = discord.Embed(
            title="Jail Confirmation",
            description=f"Are you sure you want to jail {member.mention} for the reason: {reason}?",
            color=discord.Color.gold(),
        )
        confirmation = await send_confirmation(ctx, confirmation_embed)
        if confirmation:
            await self.notify_user(member, embed)
            await ctx.send(f"{member.mention} has been jailed.")
            log_embed = discord.Embed(
                title=f"{member} has been jailed",
                description=f"Reason: {reason}",
                color=discord.Color.red(),
            )
            await self.notify_log_channel(ctx.guild, log_embed)
        else:
            await ctx.send("Jail action cancelled.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unjail(self, ctx, member: discord.Member):
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        author = ctx.author
        channels = ctx.guild.channels

        for channel in channels:
            await channel.set_permissions(member, overwrite=None)

        embed = discord.Embed(
            title="You have been released from jail!",
            description="",
            color=discord.Color.green(),
        )
        confirmation_embed = discord.Embed(
            title="Unjail Confirmation",
            description=f"Are you sure you want to unjail {member.mention}?",
            color=discord.Color.gold(),
        )
        confirmation = await send_confirmation(ctx, confirmation_embed)
        if confirmation:
            await self.notify_user(member, embed)
            await ctx.send(f"{member.mention} has been released from jail.")
            log_embed = discord.Embed(
                title=f"{member} has been released from jail",
                description="",
                color=discord.Color.green(),
            )
            await self.notify_log_channel(ctx.guild, log_embed)
        else:
            await ctx.send("Unjail action cancelled.")
