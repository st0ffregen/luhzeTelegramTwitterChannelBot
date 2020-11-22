#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import tweepy
import re
import sys
import os
import telegram
import traceback


def initTelegramBot():
    print("initialize telegram bot")
    return telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])


def OAuth():
    auth = tweepy.OAuthHandler(os.environ['TWITTER_API_KEY'], os.environ['TWITTER_API_SECRET_KEY'])
    auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    return auth


def getLastTweet(api):
    return api.user_timeline(id="@luhze_leipzig", count=10, tweet_mode='extended')#api.me(), count=10)[i])


def getValidateTweet(tweetArray):
    validTweets = []
    for tweet in tweetArray:
        if (datetime.now() - tweet.created_at).seconds < int(os.environ['INTERVAL_SECONDS']) and \
                    (datetime.now() - tweet.created_at).days < int(os.environ['INTERVAL_DAYS']) and \
                u"\u27A1" in tweet.full_text and "https://t.co/" in tweet.full_text and \
                True in [medium['type'] == 'photo' for medium in tweet.entities['media']]:
            validTweets.append(tweet)

    return validTweets


def fetchNewTweets():
    oauth = OAuth()
    api = tweepy.API(oauth)
    validTweets = getValidateTweet(getLastTweet(api))



def main():
    print("---")
    print("starting bot")
    print("utc time now: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    bot = None

    try:
        fetchNewTweets()
        bot = initTelegramBot()

    except tweepy.error.TweepError as e:
        print(f"error while working with tweepy: {e}")
        traceback.print_exc()
        bot.send_message(chat_id=os.environ['TELEGRAM_ADMIN_CHAT_ID'],
                         text=f"error while working with tweepy: {e}")
        print("exiting")
        print(sys.exc_info())
        sys.exit(1)
    except telegram.TelegramError as e:
        print(f"error while working with telegram api: {e}")
        traceback.print_exc()
        bot.send_message(chat_id=os.environ['TELEGRAM_ADMIN_CHAT_ID'],
                         text=f"error while working with telegram api: {e}")
        print("exiting")
        print(sys.exc_info())
        sys.exit(1)

    return 0


if __name__ == "__main__":
    main()
