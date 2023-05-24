import discord
from discord.ext import commands
from interactions import InteractionClient, OptionType, ButtonStyle
from redbot.core import commands, Config
import asyncio
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

        self.interactions = InteractionClient(bot)  # Initialize the interactions

        # Register the slash commands
        @self.interactions.slash_command(name="jailset", description="Manage jail settings.")
        async def jailset(ctx, channel: OptionType.CHANNEL, log: OptionType.CHANNEL):
            await self.config.guild(ctx.guild).jail_channel.set(channel.id)
            await self.config.guild(ctx.guild).jail_log_channel.set(log.id)
            await ctx.send(f"Jail channel set to {channel.mention} and jail log channel set to {log.mention}.")

        @self.interactions.slash_command(name="jail", description="Put a user in jail.")
        async def jail(ctx, member: OptionType.USER):
            await self.jail_user(ctx, member)

        @self.interactions.slash_command(name="unjail", description="Remove a user from jail.")
        async def unjail(ctx, member: OptionType.USER):
            await self.unjail_user(ctx, member)

    async def send_confirmation_embed(self, ctx, member, action):
        embed = discord.Embed(
            title=f"{action} Confirmation",
            description=f"Are you sure you want to {action.lower()} {member.mention}?",
            color=discord.Color.blurple()
        )

        components = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": ButtonStyle.SUCCESS,
                        "label": "Confirm",
                        "custom_id": "confirm"
                    },
                    {
                        "type": 2,
                        "style": ButtonStyle.DANGER,
                        "label": "Cancel",
                        "custom_id": "cancel"
                    }
                ]
            }
        ]

        msg = await ctx.send(embed=embed, components=components)

        def check(interaction):
            return interaction.author_id == ctx.author_id and interaction.message.id == msg.id

        try:
            interaction = await self.bot.wait_for("interaction", check=check, timeout=60)
        except asyncio.TimeoutError:
            components[0]["components"][0]["disabled"] = True
            components[0]["components"][1]["disabled"] = True
            await msg.edit(embed=embed, components=components)
            return None

        await interaction.response.defer_update()

        return interaction.data["custom_id"] == "confirm"

    async def restrict_member_channels(self, guild, member):
        jail_channel = guild.get_channel(await self.config.guild(guild).jail_channel())
        for channel in guild.text_channels:
            if channel != jail_channel:
                await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))

    async def restore_member_channels(self, guild, member):
        for channel in guild.text_channels:
            await channel.set_permissions(member, overwrite=None)

    async def jail_user(self, ctx, member: discord.User):
        """
        Put a user in jail.
        """
        guild = ctx.guild
        jail_channel = guild.get_channel(await self.config.guild(guild).jail_channel())
        jail_log_channel = guild.get_channel(await self.config.guild(guild).jail_log_channel())

        if jail_channel is None or jail_log_channel is None:
            return await ctx.send("Please set the jail channel and jail log channel with the `jailset` command.")

        if member == ctx.author:
            return await ctx.send("You cannot jail yourself.")

        if member == guild.me:
            return await ctx.send("You cannot jail the bot.")

        confirmed = await self.send_confirmation_embed(ctx, member, "Jail")

        if confirmed:
            try:
                await self.restrict_member_channels(guild, member)
                await jail_channel.set_permissions(member, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
                await ctx.send(f"{member.mention} has been jailed.")
                await jail_log_channel.send(f"{ctx.author.mention} jailed {member.mention}.")
            except discord.Forbidden:
                await ctx.send("I do not have the necessary permissions to jail this user.")
        else:
            await ctx.send("Jail action cancelled.")

    async defunjail_user(self, ctx, member: discord.User):
        """
        Remove a user from jail.
        """
        guild = ctx.guild
        jail_channel = guild.get_channel(await self.config.guild(guild).jail_channel())
        jail_log_channel = guild.get_channel(await self.config.guild(guild).jail_log_channel())

        if jail_channel is None or jail_log_channel is None:
            return await ctx.send("Please set the jail channel and jail log channel with the `jailset` command.")

        if member == ctx.author:
            return await ctx.send("You cannot unjail yourself.")

        if member == guild.me:
            return await ctx.send("You cannot unjail the bot.")

        confirmed = await self.send_confirmation_embed(ctx, member, "Unjail")

        if confirmed:
            try:
                await self.restore_member_channels(guild, member)
                await ctx.send(f"{member.mention} has been unjailed.")
                await jail_log_channel.send(f"{ctx.author.mention} unjailed {member.mention}.")
            except discord.Forbidden:
                await ctx.send("I do not have the necessary permissions to unjail this user.")
        else:
            await ctx.send("Unjail action cancelled.")
