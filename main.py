from typing import Callable, Iterable, Any, Awaitable

import utils.settings as settings

import discord
from discord.app_commands.tree import CommandTree
from discord.ext import commands

from dotenv import load_dotenv
from logging import getLogger

load_dotenv()
API_KEY = settings.DISCORD_API_SECRET

settings.set_loggers()

logger = getLogger("bot")


class Bot(commands.Bot):
    def __init__(
        self,
        command_prefix: Iterable[str]
        | str
        | Callable[
            [commands.Bot, discord.Message],
            Iterable[str] | str | Awaitable[Iterable[str] | str],
        ],
        *,
        tree_cls: CommandTree[Any] = CommandTree,
        description: str | None = None,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        super().__init__(
            command_prefix,
            tree_cls=tree_cls,
            description=description,
            intents=intents,
            **options,
        )

        self.initial_extensions = settings.COGS

    async def setup_hook(self):
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                logger.error(f"Error loading extension {extension}: {e}")

    async def on_ready(self):
        logger.info("Bot is Up and ready!")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")

        except Exception as e:
            logger.error(e)

        await self.change_presence(
            activity=discord.Game(name="Hypixel API shitting"),
            status=discord.Status.dnd,
        )


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = Bot(command_prefix="pls", intents=intents)

    bot.run(settings.DISCORD_API_SECRET)
