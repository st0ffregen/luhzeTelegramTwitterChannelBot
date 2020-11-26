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
    return api.user_timeline(id=api.me(), count=5, tweet_mode='extended')


def getValidateTweet(tweetArray):
    print("validate tweets")
    intervalSeconds = int(os.environ['INTERVAL_SECONDS'])
    intervalDays = int(os.environ['INTERVAL_DAYS'])

    validTweets = []
    for tweet in tweetArray:
        if (datetime.now() - tweet.created_at).seconds <= intervalSeconds and \
                    (datetime.now() - tweet.created_at).days <= intervalDays and \
                u"\u27A1" in tweet.full_text and "https://t.co/" in tweet.full_text and \
                True in [medium['type'] == 'photo' for medium in tweet.entities['media']] and \
                tweet.in_reply_to_status_id is None:
            validTweets.append(tweet)

    return validTweets


def resolveUserMentions(splitTweetArray):
    print("resolve user mentions")
    for tweet in splitTweetArray:
        for user in tweet['tweet'].entities['user_mentions']:
            screenName = user['screen_name']
            tweet['teaser'] = tweet['teaser'].replace("@" + screenName, '<a href="https://twitter.com/' + screenName + '">@' + screenName + '</a>')
    return splitTweetArray


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
    print("fetch new tweets")
    oauth = OAuth()
    api = tweepy.API(oauth)
    lastTweets = getLastTweet(api)
    validTweets = getValidateTweet(lastTweets)
    if len(validTweets) == 0:
        print("no new tweets in feed found")
        return []
    splitTweetArray = splitTweetInParts(validTweets, bot, telegramAdminChatId)
    return resolveUserMentions(splitTweetArray)


def craftText(tweet):
    if tweet['pictureCredits'] is None:
        text = "\n" + tweet['teaser'] + "\n\n" + u"\u27A1" + " " + tweet['linkToArticle']
    else:
        text = "\n" + tweet['teaser'] + "\n\n" + u"\u27A1" + " " + tweet['linkToArticle'] + "\n\n" + u"\U0001F4F8" + " " + tweet['pictureCredits']

    return text


def sendTweetToTelegram(bot, tweetArray):
    print("send " + str(len(tweetArray)) + " tweets to telegram")
    channelId = os.environ['TELEGRAM_CHANNEL_ID']
    for tweet in tweetArray:
        bot.send_photo(chat_id=channelId, photo=tweet['pictureLink'], caption= craftText(tweet), parse_mode=telegram.ParseMode.HTML)
    return 0


def main():
    print("---")
    print("starting bot")
    print("utc time now: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    telegramAdminChatId = os.environ['TELEGRAM_ADMIN_CHAT_ID']

    bot = None

    try:
        bot = initTelegramBot()
        newTweets = fetchNewTweets(bot, telegramAdminChatId)
        sendTweetToTelegram(bot, newTweets)

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
