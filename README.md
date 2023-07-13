# luhzeTelegramTwitterChannelBot
Dieser Bot ist deprecated, da die Free Tier von Twitter keine Reads mehr erlaubt.

Veröffentlicht Artikel-Tweets von luhze in einen Telegram Channel

# Build
```
docker build -t python-telegram-channel-bot ./bot
```

# Live
```
docker run -it -v "$(pwd)/bot:/usr/src/app" --rm --env-file .env --name python-telegram-channel-bot-running python-telegram-channel-bot
```