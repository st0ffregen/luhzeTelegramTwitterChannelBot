#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import tweepy
import sys
import os
import telegram
import traceback
import feedparser


def checkIfLinkIsInFeed(link):
    print("read in feed")
    NewsFeed = feedparser.parse("https://luhze.de/rss")
    entries = NewsFeed.entries

    for entry in entries:
        if entry.link.strip() == link:
            return True

    return False


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


def getValidateTweet(tweetArray, intervalSeconds, intervalDays):
    print("validate tweets")

    validTweets = []
    for tweet in tweetArray:
        if (datetime.now() - tweet.created_at).seconds <= intervalSeconds and \
                    (datetime.now() - tweet.created_at).days <= intervalDays and \
                u"\u27A1" in tweet.full_text and "https://t.co/" in tweet.full_text and \
                True in [medium['type'] == 'photo' for medium in tweet.entities['media']] and \
                tweet.in_reply_to_status_id is None and checkIfLinkIsInFeed(tweet.entities['urls'][0]['expanded_url'].strip()):
            validTweets.append(tweet)

    return validTweets


def resolveUserMentions(tweetObjectArray):
    print("resolve user mentions")
    for tweet in tweetObjectArray:
        for user in tweet['tweet'].entities['user_mentions']:
            screenName = user['screen_name']
            tweet['text'] = tweet['text'].replace("@" + screenName, '<a href="https://twitter.com/' + screenName + '">@' + screenName + '</a>')
    return tweetObjectArray


def craftTweetObjectArray(tweetArray):
    tweetObjectArray = []
    for tweet in tweetArray:
        text = tweet.full_text.strip()
        pictureLink = tweet.entities['media'][0]['media_url_https'].strip()
        linkToArticle = tweet.entities['urls'][0]['expanded_url'].strip()
        linkToArticleShort = tweet.entities['urls'][0]['display_url'].strip()

        tweetObjectArray.append({'tweet': tweet, 'text': text, 'pictureLink': pictureLink,
                                'linkToArticle': addATagToLink(linkToArticle, linkToArticleShort)})

    return tweetObjectArray


def addATagToLink(linkToArticle, linkToArticleShort):
    return "<a href=\"" + linkToArticle + "\">" + linkToArticleShort + "</a>"


def removeLinkToTweet(tweetObjectArray):
    for tweet in tweetObjectArray:
        print("remove " + tweet['tweet'].extended_entities['media'][0]['url'].strip())
        tweet['text'] = tweet['text'].replace(tweet['tweet'].extended_entities['media'][0]['url'].strip(), "").strip()

    return tweetObjectArray


def replaceLinkToArticleWithLuhzeLink(tweetObjectArray):
    for tweet in tweetObjectArray:
        tweet['text'] = tweet['text'].replace(tweet['tweet'].entities['urls'][0]['url'].strip(), tweet['linkToArticle']).strip()

    return tweetObjectArray


def fetchNewTweets(intervalSeconds, intervalDays):
    print("fetch new tweets")
    api = doAuth()
    lastTweets = getLastTweet(api)
    validTweets = getValidateTweet(lastTweets, intervalSeconds, intervalDays)
    if len(validTweets) == 0:
        print("no new tweets in feed found")
        return []
    tweetObjectArray = craftTweetObjectArray(validTweets)
    resolvedUserMentionsArray = resolveUserMentions(tweetObjectArray)
    removedUrlArray = removeLinkToTweet(resolvedUserMentionsArray)
    replacedLinkArray = replaceLinkToArticleWithLuhzeLink(removedUrlArray)
    return replacedLinkArray


def sendTweetToTelegram(bot, tweetArray):
    print("send " + str(len(tweetArray)) + " tweets to telegram")
    channelId = os.environ['TELEGRAM_CHANNEL_ID']
    for tweet in tweetArray:
        bot.send_photo(chat_id=channelId, photo=tweet['pictureLink'], caption=tweet['text'], parse_mode=telegram.ParseMode.HTML)
    return 0


def main():
    print("---")
    print("starting bot")
    print("utc time now: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    telegramAdminChatId = os.environ['TELEGRAM_ADMIN_CHAT_ID']
    intervalSeconds = int(os.environ['INTERVAL_SECONDS'])
    intervalDays = int(os.environ['INTERVAL_DAYS'])

    bot = None

    try:
        newTweets = fetchNewTweets(intervalSeconds, intervalDays)
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
