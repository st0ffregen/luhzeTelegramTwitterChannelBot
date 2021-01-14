#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import unittest
import tweepy
import re
import sys
import os
import telegram
import traceback
from dotenv import load_dotenv
from bot import main
import re

load_dotenv()


class TestBot(unittest.TestCase):

    api = None
    bot = None

    # natuerlich nicht ganz best practice weil die aus production sind und es durchaus sein kann, dass sie z.b. noch geliked werden
    statusWithURLsToResolveString = "1331600631904264193"
    statusAdvertisingArticleString = "1315947779739574280"

    @classmethod
    def setUpClass(cls) -> None:
        cls.bot = main.initTelegramBot()
        cls.api = main.doAuth()
        cls.statusWithURLsToResolve = cls.api.get_status(cls.statusWithURLsToResolveString)
        cls.statusAdvertisingArticle = cls.api.get_status(cls.statusAdvertisingArticleString)

    def test_init_bot(self):
        self.assertIsNotNone(self.bot)

    def test_doAuth(self):
        self.assertIsNotNone(self.api)

    def test_get_last_tweet(self):
        lastTweets = main.getLastTweet(self.api)
        self.assertIsInstance(lastTweets, list)
        for tweet in lastTweets:
            print(tweet.full_text)
            self.assertIsInstance(tweet, tweepy.Status)

    def test_get_validate_tweet(self):
        self.assertFalse(main.getValidateTweet([self.statusWithURLsToResolve]))
        self.assertFalse(main.getValidateTweet([self.statusAdvertisingArticle]))


    def test_get_photographer(self):
        # not sure why i do not just assign photographerName to splitOnCameraSign[1]
        self.assertEqual("Mohamad Lee", main.getPhotographer("Mohamad Lee"))

    def test_split_tweet_in_parts(self):
        pass

    def test_resolve_user_mentions(self):
        resolvedStatusArray = main.resolveUserMentions([self.statusWithURLsToResolve, self.statusAdvertisingArticle])
        self.assertTrue(resolvedStatusArray[0]['tweet'].entities['user_mentions'])
        self.assertFalse(resolvedStatusArray[1]['tweet'].entities['user_mentions'])

if __name__ == "__main__":
    unittest.main()
