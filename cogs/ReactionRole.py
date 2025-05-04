import discord
from discord.ext import commands


class ReactionRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # TODO: Change these variables to the correct ones
        self.TARGET_MESSAGE = 1  # Change according to what message to check
        self.EMOJI = "😀"  # Change emoji according to message
        self.ROLE_ID = 1  # ID of role to add

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member != self.TARGET_MESSAGE:
            return

        if str(payload.emoji) != self.EMOJI:
            return

        if payload.guild_id is None:
            embed = discord.Embed(
                description="Something went wrong, try again later",
                color=discord.Color.red(),
            )
            return await payload.member.send(embed=embed)

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(self.ROLE_ID)
        member = guild.get_member(payload.user_id)

        if not role or not member or member.bot:
            return

        await member.add_roles(role)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRole(bot))
