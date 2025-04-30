# env_test.py
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
print("Loading:", env_path)
load_dotenv(dotenv_path=env_path)

print("DISCORD_API_KEY =", os.getenv("DISCORD_API_KEY"))
