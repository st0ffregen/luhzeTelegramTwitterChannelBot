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

# natuerlich nicht ganz best practice weil die aus production sind und es durchaus sein kann, dass sie z.b. noch geliked werden
statusWithURLsToResolve = "1331600631904264193"

load_dotenv()


class TestBot(unittest.TestCase):

    fileName = os.environ['ID_FILE']
    api = None

    @classmethod
    def setUpClass(cls) -> None:
        oauth = main.OAuth()
        cls.api = tweepy.API(oauth)

    def test_init_bot(self):
        self.assertIsNotNone(main.initTelegramBot())

    def test_oauth(self):
        self.assertIsNotNone(TestBot.api)

    def test_get_last_tweet(self):

        self.assertIsInstance(main.getLastTweet(api))

if __name__ == "__main__":
    unittest.main()
