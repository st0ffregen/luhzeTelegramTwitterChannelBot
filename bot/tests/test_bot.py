#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import unittest
import tweepy
from dotenv import load_dotenv
from bot import main

load_dotenv()


class TestBot(unittest.TestCase):
    api = None
    bot = None

    # natuerlich nicht ganz best practice weil die aus production sind und es durchaus sein kann, dass sie z.b. noch geliked werden
    statusWithCreditsURLsToResolve = {"id": "1331600631904264193",
                                      "text": "Für Menschen mit Behinderungen kann es eine"
                                              " Herausforderung sein, das passende Sportangebot "
                                              "zu finden. Das sächsische Projekt „miss“ setzt sich"
                                              " deswegen für mehr Inklusion im Sport ein.",
                                      "url": "<a href=\"https://www.luhze.de/2020/11/25/barriere-frei/\">luhze.de/2020/11/25/bar…</a>",
                                      "pictureLink": "https://pbs.twimg.com/media/EnrLd-6XcAEm7Na.jpg",
                                      "credits": "Andi Weiland, <a href=\"http://Gesellschaftsbilder.de\">Gesellschaftsbilder</a>"}

    statusWithUserMentionsToResolve = {"id": "1320781058774806529",
                                       "text": "Protest gegen Jörg Baberowski: Der Historiker aus Berlin hielt am "
                                               "Donnerstag im Paulinum der "
                                               "<a href=\"https://twitter.com/UniLeipzig\">@UniLeipzig</a> einen Vortrag"
                                               " zu Gewaltmechanismen. Der Stura (<a "
                                               "href=\"https://twitter.com/StuRa_UL\">@StuRa_UL</a>) der Universität"
                                               " hatte seine Ausladung gefordert.",
                                       "url": "<a href=\"https://www.luhze.de/2020/10/26/protest-gegen-joerg-baberowski/\">luhze.de/2020/10/26/pro…</a>",
                                       "pictureLink": "https://pbs.twimg.com/media/ElRbFNCXEAQ4u6Q.jpg",
                                       "credits": None}

    statusAdvertisingArticle = {"id": "1315947779739574280",
                                "text": "Die Mosaic-Arktisexpedition untersuchte den Zustand der Natur rund um den "
                                        "Nordpol. luhze-Redakteur Niclas Stoffregen sprach mit dem Leipziger "
                                        "Meteorologen Manfred Wen­disch, der im Flugzeug dabei war.",
                                "url": "<a href=\"https://www.luhze.de/2020/10/12/die-expedition-ist-ein-meilenstein/\">luhze.de/2020/10/12/die…</a>",
                                "pictureLink": "https://pbs.twimg.com/media/EkMu0AaXYAAwoH4.jpg",
                                "credits": "Stephan Schön / Sächsische Zeitung"}

    statusIsDifferentWithoutPictureId = "1309124710970667009"
    statusIsDifferentWithPictureId = "1349612228559908866"

    @classmethod
    def setUpClass(cls) -> None:
        cls.bot = main.initTelegramBot()
        cls.api = main.doAuth()
        cls.statusWithCreditsURLsToResolveTweet = cls.api.get_status(cls.statusWithCreditsURLsToResolve['id'],
                                                                     tweet_mode="extended")
        cls.statusWithUserMentionsToResolveTweet = cls.api.get_status(cls.statusWithUserMentionsToResolve['id'],
                                                                      tweet_mode="extended")
        cls.statusAdvertisingArticleTweet = cls.api.get_status(cls.statusAdvertisingArticle['id'],
                                                               tweet_mode="extended")
        cls.statusIsDifferentWithoutPictureTweet = cls.api.get_status(cls.statusIsDifferentWithoutPictureId,
                                                                      tweet_mode="extended")
        cls.statusIsDifferentWithPictureTweet = cls.api.get_status(cls.statusIsDifferentWithPictureId,
                                                                   tweet_mode="extended")

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
        self.assertFalse(main.getValidateTweet([self.statusWithCreditsURLsToResolveTweet]))
        self.assertFalse(main.getValidateTweet([self.statusAdvertisingArticleTweet]))
        self.assertFalse(
            main.getValidateTweet([self.statusIsDifferentWithoutPictureTweet, self.statusIsDifferentWithPictureTweet]))

    def test_split_tweet_in_parts(self):
        splitTweet = main.splitTweetInParts([self.statusWithCreditsURLsToResolveTweet, self.statusAdvertisingArticleTweet])
        self.assertIsInstance(splitTweet, list)
        # check text
        self.assertEqual(self.statusWithCreditsURLsToResolve['text'], splitTweet[0]['teaser'])
        self.assertEqual(self.statusAdvertisingArticle['text'], splitTweet[1]['teaser'])
        # check link to picture
        self.assertEqual(self.statusWithCreditsURLsToResolve['pictureLink'], splitTweet[0]['pictureLink'])
        self.assertEqual(self.statusAdvertisingArticle['pictureLink'], splitTweet[1]['pictureLink'])
        # check link to article
        self.assertEqual(self.statusWithCreditsURLsToResolve['url'], splitTweet[0]['linkToArticle'])
        self.assertEqual(self.statusAdvertisingArticle['url'], splitTweet[1]['linkToArticle'])
        # check picture credits
        # self.assertEqual(self.statusWithURLsToResolve['credits'], splitTweet[0]['pictureCredits'])
        self.assertEqual(self.statusAdvertisingArticle['credits'], splitTweet[1]['pictureCredits'])

    def test_resolve_user_mentions(self):
        splitTweet = main.splitTweetInParts(
            [self.statusWithCreditsURLsToResolveTweet, self.statusWithUserMentionsToResolveTweet])
        userMentionsArray = main.resolveUserMentions(splitTweet)
        self.assertIsInstance(userMentionsArray, list)
        self.assertEqual(self.statusWithCreditsURLsToResolve['text'], userMentionsArray[0]['teaser'])
        self.assertEqual(self.statusWithUserMentionsToResolve['text'], userMentionsArray[1]['teaser'])

    def test_fetch_new_tweets(self):
        # kann sein, dass gerade ein artikel tweet hochgeladen wurde, dann schlägt der test fehl
        self.assertFalse(main.fetchNewTweets())

    def test_send_tweet_to_telegram(self):
        splitTweet = main.splitTweetInParts([self.statusWithCreditsURLsToResolveTweet,
                                             self.statusWithUserMentionsToResolveTweet,
                                             self.statusAdvertisingArticleTweet])
        userMentionsArray = main.resolveUserMentions(splitTweet)
        self.assertEqual(0, main.sendTweetToTelegram(self.bot, userMentionsArray))

    def test_check_if_link_is_in_feed(self):
        self.assertFalse(main.checkIfLinkIsInFeed("https://www.luhze.de/2020/11/25/barriere-frei/"))


if __name__ == "__main__":
    unittest.main()
