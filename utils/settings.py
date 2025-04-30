import asyncio
from aiofiles.os import listdir
from os import getenv
from loggers.loggers import setup_loggers


async def get_cogs(path: str, prefix: str):
    try:
        files = await listdir(path)
        return [
            f"{prefix}.{f[:-3]}"
            for f in files
            if f.endswith(".py") and f != "__init__.py"
        ]
    except FileNotFoundError:
        return []


async def return_cogs():
    tasks = [
        get_cogs("cogs", "cogs"),
    ]

    (NORMAL_COGS,) = await asyncio.gather(*tasks)

    COGS = NORMAL_COGS

    return COGS


def get_all_cogs():
    return asyncio.run(return_cogs())


def set_loggers():
    return asyncio.run(setup_loggers())


COGS = get_all_cogs()
DISCORD_API_SECRET = getenv("DISCORD_API_KEY")
LOGGING_CHANNEL = getenv("LOGGING_CHANNEL")

# Validate presence
assert DISCORD_API_SECRET != "1", "MISSING DISCORD API KEY"

# Validate LOGGING_CHANNEL is a digit and cast it
assert LOGGING_CHANNEL and LOGGING_CHANNEL.isdigit(), "INVALID LOGGING CHANNEL"
LOGGING_CHANNEL = int(LOGGING_CHANNEL)
