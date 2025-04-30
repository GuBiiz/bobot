# 🤖 Bo Bot

**Bo Bot** is an all-purpose Discord bot built in Python. It's the main bot powering the [open-sorce](https://discord.com/) community server — handling moderation, logging, utility commands, and more.

---

## 📌 Features

- 🔨 **Moderation** — kick, ban, warn, purge, and role management
- 🧾 **Logging** — user joins/leaves, message edits/deletes, and command usage
- 🛠️ **Utility Commands** — uptime, server info, user info, and more
- 🎮 **Fun & Custom Commands** — memes, jokes, polls, etc.
- 🔐 **Permission Checks** — ensures only trusted roles can perform sensitive actions
- 🌐 **Extensible** — modular design allows quick addition of new commands

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/bo-bot.git
cd bo-bot
```

### 2. Set up the environment

Install dependencies

```bash
python3.13 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in your root directory

```
DISCORD_API_KEY=your_discord_bot_token
LOGGING_CHANNEL=your_logging_channel_id
```

See `.env.example` for a reference

### 3. Run the bot

```bash
python main.py
```

# 🤝 Contributing

Feel free to open issues or PRs — contributions are welcome!

# ⚠️ Disclaimer

This bot is built for the `open-sorce` Discord server.
Use Bo Bot responsibly. Abuse of moderation commands may result in server penalties.
