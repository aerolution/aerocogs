import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
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

        self.slash = SlashCommand(bot, sync_commands=True)  # Initialize the slash commands

        # Register the slash commands
        self.slash.slash(name="jailset", description="Manage jail settings.", options=[
            create_option(
                name="channel",
                description="Set the jail channel.",
                option_type=7,
                required=True
            ),
            create_option(
                name="log",
                description="Set the jail log channel.",
                option_type=7,
                required=True
            )
        ], scope=self)
        self.slash.slash(name="jail", description="Put a user in jail.", options=[
            create_option(
                name="member",
                description="The user to jail.",
                option_type=6,
                required=True
            )
        ], scope=self)
        self.slash.slash(name="unjail", description="Remove a user from jail.", options=[
            create_option(
                name="member",
                description="The user to unjail.",
                option_type=6,
                required=True
            )
        ], scope=self)

    async def send_confirmation_embed(self, ctx, member, action):
        embed = discord.Embed(
            title=f"{action} Confirmation",
            description=f"Are you sure you want to {action.lower()} {member.mention}?",
            color=discord.Color.blurple()
        )

        action_row = create_actionrow(
            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
        )

        msg = await ctx.send(embed=embed, components=[action_row])

        def check(interaction):
            return interaction.author_id == ctx.author_id and interaction.message.id == msg.id

        try:
            button_ctx = await wait_for_component(self.bot, components=action_row, check=check, timeout=60)
        except asyncio.TimeoutError:
            action_row = create_actionrow(
                create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm", disabled=True),
                create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel", disabled=True)
            )
            await msg.edit(embed=embed, components=[action_row])
            return None

        await button_ctx.defer(edit_origin=True)

        return button_ctx.custom_id == "confirm"

    async def restrict_member_channels(self, guild, member):
        jail_channel = guild.get_channel(await self.config.guild(guild).jail_channel())
        for channel in guild.text_channels:
            if channel != jail_channel:
                await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))

    async def restore_member_channels(self, guild, member):
        for channel in guild.text_channels:
            await channel.set_permissions(member, overwrite=None)

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
        await ctx.send(f"Jail channel set to {channel.mention}.")

    @jailset.command(name="log")
    async def jailset_log(self, ctx, channel: discord.TextChannel):
        """
        Set the jail log channel.
        """
        await self.config.guild(ctx.guild).jail_log_channel.set(channel.id)
        await ctx.send(f"Jail log channel set to {channel.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member:discord.Member):
        """
        Put a user in jail.
        """
        jail_channel = ctx.guild.get_channel(await self.config.guild(ctx.guild).jail_channel())
        jail_log_channel = ctx.guild.get_channel(await self.config.guild(ctx.guild).jail_log_channel())

        if jail_channel is None or jail_log_channel is None:
            return await ctx.send("Please set the jail channel and jail log channel with the `jailset` command.")

        if member == ctx.author:
            return await ctx.send("You cannot jail yourself.")

        if member == ctx.guild.me:
            return await ctx.send("You cannot jail the bot.")

        confirmed = await self.send_confirmation_embed(ctx, member, "Jail")

        if confirmed:
            try:
                await self.restrict_member_channels(ctx.guild, member)
                await jail_channel.set_permissions(member, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
                await ctx.send(f"{member.mention} has been jailed.")
                await jail_log_channel.send(f"{ctx.author.mention} jailed {member.mention}.")
            except discord.Forbidden:
                await ctx.send("I do not have the necessary permissions to jail this user.")
        else:
            await ctx.send("Jail action cancelled.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unjail(self, ctx, member: discord.Member):
        """
        Remove a user from jail.
        """
        jail_channel = ctx.guild.get_channel(await self.config.guild(ctx.guild).jail_channel())
        jail_log_channel = ctx.guild.get_channel(await self.config.guild(ctx.guild).jail_log_channel())

        if jail_channel is None or jail_log_channel is None:
            return await ctx.send("Please set the jail channel and jail log channel with the `jailset` command.")

        if member == ctx.author:
            return await ctx.send("You cannot unjail yourself.")

        if member == ctx.guild.me:
            return await ctx.send("You cannot unjail the bot.")

        confirmed = await self.send_confirmation_embed(ctx, member, "Unjail")

        if confirmed:
            try:
                await self.restore_member_channels(ctx.guild, member)
                await ctx.send(f"{member.mention} has been unjailed.")
                await jail_log_channel.send(f"{ctx.author.mention} unjailed {member.mention}.")
            except discord.Forbidden:
                await ctx.send("I do not have the necessary permissions to unjail this user.")
        else:
            await ctx.send("Unjail action cancelled.")
