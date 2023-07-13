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
    auth = tweepy.OAuth1UserHandler(os.environ['TWITTER_API_KEY'], os.environ['TWITTER_API_SECRET_KEY'], os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)
    return api


def getLastTweet(api):
    print("get last tweets")
    return api.user_timeline(id="luhze_leipzig", count=5, tweet_mode='extended')


def getValidateTweet(tweetArray, intervalSeconds, intervalDays, upperTimeBound):
    print("validate tweets")

    validTweets = []
    newestArticleLinksFromLuhze = getLinksToLuhzeArticles()

    for tweet in tweetArray:
        if not (upperTimeBound - tweet.created_at).seconds <= intervalSeconds:
            print('tweet ' + tweet.id_str + ' older than ' + str(intervalSeconds) + ' seconds')
            continue

        if not (upperTimeBound - tweet.created_at).days <= intervalDays:
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


def fetchNewTweets(intervalSeconds, intervalDays, upperTimeBound, api):
    print("fetch new tweets")
    lastTweets = getLastTweet(api)
    validTweets = getValidateTweet(lastTweets, intervalSeconds, intervalDays, upperTimeBound)
    if len(validTweets) == 0:
        print('no valid tweets')
        return []
    tweetObjectArray = craftTweetObjectArray(validTweets)
    notSentValidTweets = getNotSentArticles(tweetObjectArray)
    resolvedUserMentionsArray = resolveUserMentions(notSentValidTweets)
    removedUrlArray = removeLinkToTweet(resolvedUserMentionsArray)
    replacedLinkArray = resolveUrls(removedUrlArray)
    resolvedHashtagsArray = resolveHashtags(replacedLinkArray)
    return resolvedHashtagsArray


def getNotSentArticles(tweetObjectArray):
    try:
        file = open('sentTweetsList', 'r')
        return compareFileContentToTweetArray(file, tweetObjectArray)
    except FileNotFoundError:
        newFile = open('sentTweetsList', 'w')
        newFile.close()
        file = open('sentTweetsList', 'r')
        return compareFileContentToTweetArray(file, tweetObjectArray)


def compareFileContentToTweetArray(file, tweetObjectArray):
    notSentTweets = []
    content = file.read().splitlines()
    for tweetObject in tweetObjectArray:
        if tweetObject['linkToArticle'].split('">')[0].replace('<a href="', '').strip() not in content:
            notSentTweets.append(tweetObject)
        else:
            print('tweet already posted to channel')

    file.close()

    return notSentTweets


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


def writeTweetsToFile(tweetObjectArray):
    file = open('sentTweetsList', 'a')
    for tweetObject in tweetObjectArray:
        file.write(tweetObject['linkToArticle'].split('">')[0].replace('<a href="', '').strip() + '\n')

    file.close()


def main():
    startingTime = datetime.utcnow()

    print("---")
    print("starting bot")
    print("utc time now: " + startingTime.strftime('%Y-%m-%d %H:%M:%S'))

    intervalSeconds = int(os.environ['INTERVAL_SECONDS'])
    intervalDays = int(os.environ['INTERVAL_DAYS'])

    try:
        api = doAuth()
        newTweets = fetchNewTweets(intervalSeconds, intervalDays, startingTime, api)
        if len(newTweets) > 0:
            bot = initTelegramBot()
            sendTweetToTelegram(bot, newTweets)
            writeTweetsToFile(newTweets)

    except Exception as e:
        print(f"error: {e}")
        traceback.print_exc()
        print("exiting")
        print(sys.exc_info())
        sys.exit(1)

    return 0


if __name__ == "__main__":
    main()
