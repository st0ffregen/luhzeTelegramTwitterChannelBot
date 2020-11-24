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
    return api.user_timeline(id="@luhze_leipzig", count=30, tweet_mode='extended')#api.me(), count=10)[i])


def getValidateTweet(tweetArray):
    print("validate tweets")
    validTweets = []
    for tweet in tweetArray:
        if (datetime.now() - tweet.created_at).seconds < int(os.environ['INTERVAL_SECONDS']) and \
                    (datetime.now() - tweet.created_at).days < int(os.environ['INTERVAL_DAYS']) and \
                u"\u27A1" in tweet.full_text and "https://t.co/" in tweet.full_text and \
                True in [medium['type'] == 'photo' for medium in tweet.entities['media']]:
            validTweets.append(tweet)

    return validTweets


def resolveLinkShortener(tweetArray):
    return 0


def splitTweetInParts(tweetArray, bot, telegramAdminChatId):
    print("split tweet in parts")
    splitTweetArray = []
    for tweet in tweetArray:
        teaser = tweet.full_text.split("\n")[0].strip()
        pictureLink = tweet.entities['media'][0]['media_url_https'].strip()
        linkToArticle = tweet.entities['urls'][0]['expanded_url'].strip()
        # get credits if present
        splitOnCameraSign = tweet.full_text.split(u"\U0001F4F8")
        if len(splitOnCameraSign) > 1:
            try:
                pictureCredits = splitOnCameraSign[1].split(" ")
                photographerName = ""
                for i in range(0, len(pictureCredits)-1):
                    photographerName += " " + pictureCredits[i]

            except IndexError as e:
                print("picture credits present in the wrong format in " + tweet.entities['media'][0]['url'])
                bot.send_message(chat_id=telegramAdminChatId,
                                 text="picture credits present in the wrong format in " + tweet.entities['media'][0]['url'])
        else:
            photographerName = None
        splitTweetArray.append({'tweet': tweet, 'teaser': teaser, 'pictureLink': pictureLink,
                                'linkToArticle': linkToArticle, 'pictureCredits': photographerName})

    return splitTweetArray


def fetchNewTweets(bot, telegramAdminChatId):
    oauth = OAuth()
    api = tweepy.API(oauth)
    lastTweets = getLastTweet(api)
    validTweets = getValidateTweet(lastTweets)
    splitTweetArray = splitTweetInParts(validTweets, bot, telegramAdminChatId)
  


def main():
    print("---")
    print("starting bot")
    print("utc time now: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    telegramAdminChatId = os.environ['TELEGRAM_ADMIN_CHAT_ID']

    bot = None

    try:
        bot = initTelegramBot()
        fetchNewTweets(bot, telegramAdminChatId)


    except tweepy.error.TweepError as e:
        print(f"error while working with tweepy: {e}")
        traceback.print_exc()
        bot.send_message(chat_id=telegramAdminChatId,
                         text=f"error while working with tweepy: {e}")
        print("exiting")
        print(sys.exc_info())
        sys.exit(1)
    except telegram.TelegramError as e:
        print(f"error while working with telegram api: {e}")
        traceback.print_exc()
        bot.send_message(chat_id=telegramAdminChatId,
                         text=f"error while working with telegram api: {e}")
        print("exiting")
        print(sys.exc_info())
        sys.exit(1)

    return 0


if __name__ == "__main__":
    main()
