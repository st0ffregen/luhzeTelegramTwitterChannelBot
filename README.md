# luhzeTelegramTwitterChannelBot
Veröffentlicht Artikel-Tweets von luhze in einen Telegram Channel

# Build
```
docker build -t python-telegram-channel-bot ./bot
```

# Live
```
docker run -it --rm --env-file .env --name python-telegram-channel-bot-running python-telegram-channel-bot
```