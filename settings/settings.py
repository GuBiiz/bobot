import asyncio
import logging
from json import load
from logging.config import dictConfig
from aiofiles.os import listdir
from os import getenv, path
from dotenv import load_dotenv

load_dotenv()


async def setup_loggers():
    LOGGER_PATH = path.join(path.dirname(__file__), "loggers.json")

    try:
        with open(LOGGER_PATH) as log_configs:
            logs = load(log_configs)

        dictConfig(logs)
        logging.info("Logging configuration has been successfully loaded")
    except Exception as e:
        print(f"Error while loading logging configs {e}")
        raise


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
LOGGING_CHANNEL = int(getenv("LOGGING_CHANNEL"))

# Validate presence
assert DISCORD_API_SECRET != "1", "MISSING DISCORD API KEY"

# Validate LOGGING_CHANNEL is a digit and cast it
assert LOGGING_CHANNEL and LOGGING_CHANNEL, "INVALID LOGGING CHANNEL"
LOGGING_CHANNEL = int(LOGGING_CHANNEL)
