import discord
from redbot.core import commands, Config
import asyncio
import re
from datetime import timedelta
from discord.ui import button, View
from discord import ButtonStyle

class JailConfirmationView(View):
    def __init__(self, target_member, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_member = target_member
        self.author = author
        self.result = None

    @button(label="Confirm", style=ButtonStyle.green)
    async def confirm_button(self, button, interaction):
        if interaction.user == self.author:
            self.result = True
            self.stop()
        else:
            await interaction.response.send_message("Only the command author can interact with this message.", ephemeral=True)

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel_button(self, button, interaction):
        if interaction.user == self.author:
            self.result = False
            self.stop()
        else:
            await interaction.response.send_message("Only the command author can interact with this message.", ephemeral=True)

class Jail(commands.Cog):
    """
    Put users in a jail! (Channel.)
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"jail_channel": None, "jail_log_channel": None}
        self.config.register_guild(**default_guild)

    async def send_confirmation_embed(self, ctx, member, action):
        embed = discord.Embed(
            title=f"{action} Confirmation",
            description=f"Are you sure you want to {action.lower()} {member.mention}?",
            color=discord.Color.blurple()
        )

        view = JailConfirmationView(target_member=member, author=ctx.author, timeout=60)
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()

        # Remove the buttons after the interaction is completed.
        view.clear_items()
        await msg.edit(view=view)

        return view.result

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.group()
    async def jailset(self, ctx):
        """
        Manage jail settings.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("jailset")

    @jailset.command(name="channel")
    async def jailset_channel(self, ctx, channel: discord.TextChannel):
        """
        Set the jail channel.
        """
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        await ctx.send(f"Jail channel set to {channel.mention}")

    @jailset.command(name="log")
    async def jailset_log(self, ctx, channel: discord.TextChannel):
        """
        Set the jail log channel.
        """
        await self.config.guild(ctx.guild).jail_log_channel.set(channel.id)
        await ctx.send(f"Jail log channel set to {channel.mention}")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member: discord.Member, *args):
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_log_channel_id = await self.config.guild(ctx.guild).jail_log_channel()

        if jail_channel_id is None:
            await ctx.send("Jail channel not set.")
            return

        if jail_log_channel_id is None:
            await ctx.send("Jail log channel not set.")
            return

        jail_channel = ctx.guild.get_channel(jail_channel_id)
        jail_log_channel = ctx.guild.get_channel(jail_log_channel_id)

        if jail_channel is None or jail_log_channel is None:
            await ctx.send("Invalid jail or jail log channel.")
            return

        confirmed = await self.send_confirmation_embed(ctx, member, "Jail")
        if not confirmed:
            await ctx.send("Jail action canceled.")
            return

        overwrites = discord.PermissionOverwrite(read_messages=False, send_messages=False)
        for channel in ctx.guild.channels:
            if channel == jail_channel:
                await channel.set_permissions(member, read_messages=True, send_messages=True)
            else:
                await channel.set_permissions(member, overwrite=overwrites)

        embed = discord.Embed(
            title="Jail",
            description=f"{member.mention} has been jailed.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

        log_embed = discord.Embed(
            title="Jail Log",
            description=f"{member.mention} has been jailed by {ctx.author.mention}",
            color=discord.Color.red()
        )
        await jail_log_channel.send(embed=log_embed)

    @commands.guild_only    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unjail(self, ctx, member: discord.Member):
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_log_channel_id = await self.config.guild(ctx.guild).jail_log_channel()

        if jail_channel_id is None:
            await ctx.send("Jail channel not set.")
            return

        if jail_log_channel_id is None:
            await ctx.send("Jail log channel not set.")
            return

        jail_channel = ctx.guild.get_channel(jail_channel_id)
        jail_log_channel = ctx.guild.get_channel(jail_log_channel_id)

        if jail_channel is None or jail_log_channel is None:
            await ctx.send("Invalid jail or jail log channel.")
            return

        confirmed = await self.send_confirmation_embed(ctx, member, "Unjail")
        if not confirmed:
            await ctx.send("Unjail action canceled.")
            return

        for channel in ctx.guild.channels:
            if channel == jail_channel:
                await channel.set_permissions(member, overwrite=None)
            else:
                await channel.set_permissions(member, overwrite=None)

        embed = discord.Embed(
            title="Unjail",
            description=f"{member.mention} has been unjailed.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        log_embed = discord.Embed(
            title="Unjail Log",
            description=f"{member.mention} has been unjailed by {ctx.author.mention}",
            color=discord.Color.green()
        )
        await jail_log_channel.send(embed=log_embed)
