import logging
from logging.config import dictConfig
from json import load
from os import path


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
