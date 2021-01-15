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


def doAuth():
    print("authenticate to twitter")
    auth = tweepy.OAuthHandler(os.environ['TWITTER_API_KEY'], os.environ['TWITTER_API_SECRET_KEY'])
    auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)
    return api


def getLastTweet(api):
    print("get last tweets")
    return api.user_timeline(id="luhze_leipzig", count=5, tweet_mode='extended')


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


def splitTweetInParts(tweetArray):
    print("split tweet in parts")
    splitTweetArray = []
    for tweet in tweetArray:
        teaser = tweet.full_text.split("\n")[0].strip()
        pictureLink = tweet.entities['media'][0]['media_url_https'].strip()
        linkToArticle = tweet.entities['urls'][0]['expanded_url'].strip()
        linkToArticleShort = tweet.entities['urls'][0]['display_url'].strip()
        # get credits if present
        splitOnCameraSign = tweet.full_text.split(u"\U0001F4F8")
        photographerName = None
        if len(splitOnCameraSign) > 1:
            photographerName = ' '.join(splitOnCameraSign[1].split(' ')[:-1])

        splitTweetArray.append({'tweet': tweet, 'teaser': teaser, 'pictureLink': pictureLink,
                                'linkToArticle': addATagToLink(linkToArticle, linkToArticleShort), 'pictureCredits': photographerName})

    return splitTweetArray


def addATagToLink(linkToArticle, linkToArticleShort):
    return "<a href=\"" + linkToArticle + "\">" + linkToArticleShort + "</a>"


def fetchNewTweets():
    print("fetch new tweets")
    api = doAuth()
    lastTweets = getLastTweet(api)
    validTweets = getValidateTweet(lastTweets)
    if len(validTweets) == 0:
        print("no new tweets in feed found")
        return []
    splitTweetArray = splitTweetInParts(validTweets)
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
        newTweets = fetchNewTweets()
        bot = initTelegramBot()
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
