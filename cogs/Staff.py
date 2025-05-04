from os import name
import re
from asyncio import sleep
from datetime import timedelta
from logging import getLogger

import discord
from discord import TextChannel, app_commands
from discord.ext import commands
from discord.ext.commands import UserNotFound, MissingPermissions, BadArgument

from settings.settings import LOGGING_CHANNEL

TIME_MULTIPLIERS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
LOG = getLogger("bot")

staff = app_commands.Group(name="staff", description="Moderator utilities")


def mod_command(name: str, perm_name: str, description: str = ""):
    def decorator(func):
        func = staff.command(name=name, description=description)(func)
        func = app_commands.describe(
            member="Member to punish", reason="", duration="e.g. 10m, 2h"
        )(func)
        func = app_commands.checks.has_permissions(**{perm_name: True})(func)
        func = app_commands.checks.cooldown(1, 20)(func)
        return func

    return decorator


def parse_duration(input_str: str) -> int | None:
    """Parse strings like '10m', '2h' into seconds. Return None on failure."""
    match = re.fullmatch(r"(\d+)([smhdw])", input_str.lower())
    if not match:
        return None
    amount, unit = match.groups()
    return int(amount) * TIME_MULTIPLIERS[unit]


class Staff(commands.Cog):
    """Moderator slash commands group."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        channel = self.bot.get_channel(LOGGING_CHANNEL)

        assert isinstance(channel, TextChannel), (
            "LOGGING_CHANNEL must be a text channel"
        )
        self.log_channel: TextChannel = channel

    async def _log(
        self, ctx: discord.Interaction, action: str, member: discord.Member, **data
    ):
        msg = f"{ctx.user.mention} {action} {member.mention}"
        if data:
            extras = ", ".join(f"{k}={v}" for k, v in data.items())
            msg += f" ({extras})"
        if self.log_channel:
            return self.log_channel.send(msg)

    async def _timeout_role(
        self, member: discord.Member, role: discord.Role, duration: int
    ):
        await member.add_roles(role)
        await sleep(duration)
        await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                "You lack permissions.", ephemeral=True
            )
        elif isinstance(error, BadArgument):
            await interaction.response.send_message(
                "Bad argument: " + str(error), ephemeral=True
            )
        else:
            LOG.exception("Unhandled command error")
            await interaction.response.send_message(
                "Something went wrong.", ephemeral=True
            )

    @mod_command("voice_mute", "mute_members", "Mute someone from VC")
    async def voice_mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
        duration: str,
    ):
        """Temporarily time-out someone in voice."""
        secs = parse_duration(duration)
        if secs is None:
            return await interaction.response.send_message(
                "Invalid duration format. Use 10s/5m/2h/1d etc.", ephemeral=True
            )
        until = discord.utils.utcnow() + timedelta(seconds=secs)
        await member.edit(mute=True, timed_out_until=until, reason=reason)
        await interaction.response.send_message(
            f"{member.mention} voice-muted for {duration}", ephemeral=True
        )
        await member.send(
            f"You were voice-muted by {interaction.user} for {reason}, until {until.isoformat()}"
        )
        await self._log(
            interaction, "voice-muted", member, reason=reason, duration=duration
        )

    @mod_command("voice_unmute", "mute_members", "Member to un-muted from VC")
    async def voice_unmute(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        # Unmutes member
        await member.edit(mute=False)
        await interaction.response.send_message(
            f"{member.mention} voice-unmuted", ephemeral=True
        )
        await member.send(f"You were un-muted by {interaction.user}")
        await self._log(interaction, "voice-unmuted", member)

    @mod_command("mute", "mute_members", "Member to mute")
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
        duration: str | None = None,
    ):
        """Add a 'Muted' role, optionally for a set time."""
        if interaction.guild is None:
            return

        role = discord.utils.get(interaction.guild.roles, name="Muted")

        # If role is not found, create one
        if role is None:
            perms = discord.Permissions(
                send_messages=False, speak=False, add_reactions=False, connect=False
            )

            # Create the Muted role
            await interaction.guild.create_role(
                name="Muted",
                permissions=perms,
                colour=discord.Color.light_grey(),
                mentionable=False,
            )

            # Return a message to mod that muted role was not found, but has been created
            return await interaction.response.send_message(
                "No 'Muted' role found. Created one. Run command again to mute member",
                ephemeral=True,
            )

        # If duration is specified, mute the user according to specified time
        if duration:
            secs = parse_duration(duration)
            if secs is None:
                return await interaction.response.send_message(
                    "Bad duration format.", ephemeral=True
                )

            # Add muted role to user as a bot task
            self.bot.loop.create_task(self._timeout_role(member, role, secs))

        # Add muted role to user
        await member.add_roles(role, reason=reason)

        # Send message to Moderator that user has been muted
        await interaction.response.send_message(
            f"{member.mention} muted{' for ' + duration if duration else ''}",
            ephemeral=True,
        )

        # Send message to user that they have been muted
        await member.send(
            f"You were muted by {interaction.user} for {reason or 'no reason specified'}"
        )

        # Log the interaction
        await self._log(interaction, "muted", member, reason=reason, duration=duration)

    @staff.command(name="unmute")
    @app_commands.describe(member="Member to unmute")
    @app_commands.checks.has_permissions(mute_members=True)
    @app_commands.checks.cooldown(1, 20)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild is None:
            return

        role = discord.utils.get(interaction.guild.roles, name="Muted")

        if role:
            await member.remove_roles(role)
        await interaction.response.send_message(
            f"{member.mention} un-muted", ephemeral=True
        )
        await self._log(interaction, "un-muted", member)

    @staff.command(name="kick")
    @app_commands.describe(member="Member to kick", reason="Why?")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.cooldown(1, 20)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
    ):
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"{member.mention} kicked", ephemeral=True
        )
        await member.send(
            f"You were kicked by {interaction.user} for {reason or 'no reason specified'}"
        )
        await self._log(interaction, "kicked", member, reason=reason)

    @staff.command(name="ban")
    @app_commands.describe(member="Member to ban", reason="Why?", duration="e.g. 1d")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.cooldown(1, 20)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
        duration: str | None = None,
    ):
        if duration:
            secs = parse_duration(duration)
            if secs is None:
                return await interaction.response.send_message(
                    "Bad duration format.", ephemeral=True
                )
        await member.send(f"You were banned by {interaction.user} for {reason}")

        if interaction.guild is None:
            return

        await interaction.guild.ban(member, reason=reason)

        if duration:
            # schedule unban
            self.bot.loop.create_task(
                self._scheduled_unban(interaction.guild, member.id, secs)
            )
        await interaction.response.send_message(
            f"{member.mention} banned", ephemeral=True
        )
        await self._log(interaction, "banned", member, reason=reason, duration=duration)

    async def _scheduled_unban(self, guild: discord.Guild, user_id: int, delay: int):
        await sleep(delay)
        user = await self.bot.fetch_user(user_id)
        await guild.unban(user)

    @staff.command(name="unban")
    @app_commands.describe(user_id="User ID to unban")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.cooldown(1, 20)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        if interaction.guild is None:
            return

        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
        except (ValueError, UserNotFound):
            return await interaction.response.send_message(
                "Invalid user ID or not banned.", ephemeral=True
            )
        await interaction.response.send_message(
            f"{user.mention} un-banned", ephemeral=True
        )
        await self._log(interaction, "un-banned", user)

    @staff.command(name="clear")
    @app_commands.describe(amount="How many messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 2)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(
            f"Deleted {amount} messages.", ephemeral=True
        )
        await self._log(
            interaction, "cleared messages", interaction.user, amount=amount
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Staff(bot))
