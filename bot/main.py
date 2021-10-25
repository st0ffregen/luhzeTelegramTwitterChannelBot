#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import tweepy
import sys
import os
import telegram
import traceback
import feedparser
from dotenv import load_dotenv

load_dotenv()


def getLinksToLuhzeArticles():
    print("read in feed")
    NewsFeed = feedparser.parse("https://luhze.de/rss")
    entries = NewsFeed.entries

    linkArray = []

    for entry in entries:
        linkArray.append(entry.link.strip())

    return linkArray


def initTelegramBot():
    print("initialize telegram bot")
    if os.environ['STAGE'] == "testing":
        token = os.environ['TELEGRAM_TOKEN_TESTING']
    elif os.environ['STAGE'] == "production":
        token = os.environ['TELEGRAM_TOKEN']
    else:
        print("stage is not specified. exiting")
        sys.exit(1)

    return telegram.Bot(token=token)


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
    newestArticleLinksFromLuhze = getLinksToLuhzeArticles()

    for tweet in tweetArray:
        if not (datetime.now() - tweet.created_at).seconds <= intervalSeconds:
            print('tweet ' + tweet.id_str + ' older than ' + str(intervalSeconds) + ' seconds')
            continue

        if not (datetime.now() - tweet.created_at).days <= intervalDays:
            print('tweet ' + tweet.id_str + ' older than ' + str(intervalDays) + ' days')
            continue

        if u"\u27A1" not in tweet.full_text:
            print(u"\u27A1" + ' not in tweet ' + tweet.id_str)
            continue

        if "https://t.co/" not in tweet.full_text:
            print('no t.co link in tweet ' + tweet.id_str)
            continue

        if True not in [medium['type'] == 'photo' for medium in tweet.entities['media']]:
            print('no photo in tweet ' + tweet.id_str)
            continue

        if tweet.in_reply_to_status_id is not None:
            print('tweet ' + tweet.id_str + ' is a reply')
            continue

        if tweet.entities['urls'][0]['expanded_url'].strip() not in newestArticleLinksFromLuhze:
            print('no link to a recent luhze article in tweet ' + tweet.id_str)
            continue

        print('tweet ' + tweet.id_str + ' is valid')
        validTweets.append(tweet)

    return validTweets


def resolveUrls(tweetObjectArray):
    print("resolve urls")
    for tweet in tweetObjectArray:
        for url in tweet['tweet'].entities['urls']:
            tweet['text'] = tweet['text'].replace(url['url'],
                                                  '<a href="' + url['url'] + '">' + url['display_url'] + '</a>')
    return tweetObjectArray


def resolveHashtags(tweetObjectArray):
    print("resolve hashtags")
    for tweet in tweetObjectArray:
        for hashtag in tweet['tweet'].entities['hashtags']:
            tweet['text'] = tweet['text'].replace('#' + hashtag['text'],
                                                  '<a href="https://twitter.com/hashtag/' + hashtag[
                                                      'text'] + '?src=hashtag_click">#' + hashtag['text'] + '</a>')
    return tweetObjectArray


def resolveUserMentions(tweetObjectArray):
    print("resolve user mentions")
    for tweet in tweetObjectArray:
        for user in tweet['tweet'].entities['user_mentions']:
            screenName = user['screen_name']
            tweet['text'] = tweet['text'].replace("@" + screenName,
                                                  '<a href="https://twitter.com/' + screenName + '">@' + screenName + '</a>')
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


def fetchNewTweets(intervalSeconds, intervalDays, api, bot):
    print("fetch new tweets")
    lastTweets = getLastTweet(api)
    validTweets = getValidateTweet(lastTweets, intervalSeconds, intervalDays)
    if len(validTweets) == 0:
        print('no valid tweets')
        return []
    tweetObjectArray = craftTweetObjectArray(validTweets)
    notSentValidTweets = getNotSentArticles(bot, tweetObjectArray)
    resolvedUserMentionsArray = resolveUserMentions(notSentValidTweets)
    removedUrlArray = removeLinkToTweet(resolvedUserMentionsArray)
    replacedLinkArray = resolveUrls(removedUrlArray)
    resolvedHashtagsArray = resolveHashtags(replacedLinkArray)
    return resolvedHashtagsArray


def getNotSentArticles(bot, tweetObjects):
    notSentArticles = []

    for tweetObject in tweetObjects:
        if not isArticleAlreadyInChannel(bot, tweetObject):
            notSentArticles.append(tweetObject)

    return notSentArticles


def isArticleAlreadyInChannel(bot, tweetObject):
    updates = bot.get_updates(timeout=120)

    for update in updates:
        message = update['channel_post']['text']
        if tweetObject['linkToArticle'].split('>')[1].replace('</a', '').strip() in message:
            return True

    return False


def sendTweetToTelegram(bot, tweetArray):
    print("send " + str(len(tweetArray)) + " tweets to telegram")
    if os.environ['STAGE'] == "testing":
        channelId = os.environ['TELEGRAM_CHANNEL_ID_TESTING']
    elif os.environ['STAGE'] == "production":
        channelId = os.environ['TELEGRAM_CHANNEL_ID']
    else:
        print("stage is not specified. exiting")
        sys.exit(1)

    for tweet in tweetArray:
        bot.send_photo(chat_id=channelId, photo=tweet['pictureLink'], caption=tweet['text'],
                       parse_mode=telegram.ParseMode.HTML)
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
        api = doAuth()
        bot = initTelegramBot()
        newTweets = fetchNewTweets(intervalSeconds, intervalDays, api, bot)
        if len(newTweets) > 0:
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
