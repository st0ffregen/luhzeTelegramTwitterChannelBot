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

    statusTextToReplaceLinks = "2001 haben Engagierte das UT Connewitz, eines der ältesten Kinos Deutschlands, wieder zum Leben erweckt. Davor hat das Lichtspielhaus bereits viele andere Projekte beherbergt. ➡️https://t.co/DFwVMXDOiZ UT Connewitz https://t.co/YV2QhUABqN"

    # natuerlich nicht ganz best practice weil die aus production sind und es durchaus sein kann, dass sie z.b. noch geliked werden
    statusWithCreditsURLsToResolve = {"id": "1331600631904264193",
                                      "text": "Für Menschen mit Behinderungen kann es eine Herausforderung sein, das passende Sportangebot zu finden. Das sächsische Projekt „miss“ setzt sich deswegen für mehr Inklusion im Sport ein.\n\n" + u"\u27A1" + "️https://t.co/B7tVYURD08\n\n" + u"\U0001F4F8" + "Andi Weiland, https://t.co/JAdqeXu0ul https://t.co/kHH6abE9Kp",
                                      "textAfterUrlsResolved": "Für Menschen mit Behinderungen kann es eine Herausforderung sein, das passende Sportangebot zu finden. Das sächsische Projekt „miss“ setzt sich deswegen für mehr Inklusion im Sport ein.\n\n" + u"\u27A1" + "️<a href=\"https://t.co/B7tVYURD08\">luhze.de/2020/11/25/bar…</a>\n\n" + u"\U0001F4F8" + "Andi Weiland, <a href=\"https://t.co/JAdqeXu0ul\">Gesellschaftsbilder.de</a> https://t.co/kHH6abE9Kp",
                                      "url": "<a href=\"https://www.luhze.de/2020/11/25/barriere-frei/\">luhze.de/2020/11/25/bar…</a>",
                                      "pictureLink": "https://pbs.twimg.com/media/EnrLd-6XcAEm7Na.jpg",
                                      "credits": "Andi Weiland, <a href=\"http://Gesellschaftsbilder.de\">Gesellschaftsbilder.de</a>"}

    statusWithUserMentionsToResolve = {"id": "1320781058774806529",
                                       "text": "Protest gegen Jörg Baberowski: Der Historiker aus Berlin hielt am "
                                               "Donnerstag im Paulinum der @UniLeipzig einen Vortrag zu Gewaltmechanismen. Der Stura"
                                               " (@StuRa_UL) der Universität"
                                               " hatte seine Ausladung gefordert.\n\n" + u"\u27A1" + "️https://t.co/Aqu9KR7Cfw https://t.co/FM735bEzED",
                                       "textAfterUserMentionsResolved": "Protest gegen Jörg Baberowski: Der Historiker aus Berlin hielt am "
                                               "Donnerstag im Paulinum der "
                                               "<a href=\"https://twitter.com/UniLeipzig\">@UniLeipzig</a> einen Vortrag"
                                               " zu Gewaltmechanismen. Der Stura (<a "
                                               "href=\"https://twitter.com/StuRa_UL\">@StuRa_UL</a>) der Universität"
                                               " hatte seine Ausladung gefordert.\n\n" + u"\u27A1" + "️https://t.co/Aqu9KR7Cfw https://t.co/FM735bEzED",
                                       "textAfterUrlsResolved": "Protest gegen Jörg Baberowski: Der Historiker aus Berlin hielt am "
                                               "Donnerstag im Paulinum der @UniLeipzig einen Vortrag"
                                               " zu Gewaltmechanismen. Der Stura (@StuRa_UL) der Universität"
                                               " hatte seine Ausladung gefordert.\n\n" + u"\u27A1" + "️<a href=\"https://t.co/Aqu9KR7Cfw\">luhze.de/2020/10/26/pro…</a> https://t.co/FM735bEzED",
                                       "url": "<a href=\"https://www.luhze.de/2020/10/26/protest-gegen-joerg-baberowski/\">luhze.de/2020/10/26/pro…</a>",
                                       "pictureLink": "https://pbs.twimg.com/media/ElRbFNCXEAQ4u6Q.jpg",
                                       "credits": None}

    statusAdvertisingArticle = {"id": "1315947779739574280",
                                "text": "Die Mosaic-Arktisexpedition untersuchte den Zustand der Natur rund um den "
                                        "Nordpol. luhze-Redakteur Niclas Stoffregen sprach mit dem Leipziger "
                                        "Meteorologen Manfred Wen­disch, der im Flugzeug dabei war.\n\n" + u"\u27A1" +
                                        "️https://t.co/Fu6NTSjb9g\n\n" + u"\U0001F4F8" + "Stephan Schön / Sächsische "
                                                                                         "Zeitung https://t.co/eBiQ3F9rIU",
                                "url": "<a href=\"https://www.luhze.de/2020/10/12/die-expedition-ist-ein-meilenstein/\">luhze.de/2020/10/12/die…</a>",
                                "pictureLink": "https://pbs.twimg.com/media/EkMu0AaXYAAwoH4.jpg",
                                "credits": "Stephan Schön / Sächsische Zeitung"}

    statusNotAdvertisingArticleWithoutPicture = {"id": "1309124710970667009"}
    statusNotAdvertisingArticleWithPicture = {"id": "1349612228559908866"}
    statusWithTextAfterPhotoCredits = {"id": "1290923771818389506"}
    statusWithTextAfterLinkAndWithoutPhotoCredits = {"id": "1286978882349006848"}
    statusWithHashtagsInTextAndTextAndHashtagAfterLinkWithoutPhotoCredits = {"id": "1282685691005149189",
                                                                             "text": "Wegen der Coronakrise kann die <a href=\"https://twitter.com/hashtag/FridaysForFuture?src=hashtag_click\">#FridaysForFuture</a>-Bewegung nicht wie gewohnt auf der Straße demonstrieren. luhze-Redakteurin Nele Sikau sprach mit Aktivistin Annelie Berger über die Zukunft von @F4F_Leipzig.\n\n" + u"\u27A1" + "️https://t.co/Kn6rIv6QkY\n\nInterview aus der Juli-Ausgabe\n\n<a href=\"https://twitter.com/hashtag/Leipzig?src=hashtag_click\">#Leipzig</a> https://t.co/wCALUzqbzx"}
    statusIsNormal = {"id": "1362451829473296394"}

    @classmethod
    def setUpClass(cls) -> None:
        cls.bot = main.initTelegramBot()
        cls.api = main.doAuth()
        cls.allExampleTweets = []
        cls.statusWithCreditsURLsToResolveTweet = cls.api.get_status(cls.statusWithCreditsURLsToResolve['id'],
                                                                     tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusWithCreditsURLsToResolveTweet)
        cls.statusWithUserMentionsToResolveTweet = cls.api.get_status(cls.statusWithUserMentionsToResolve['id'],
                                                                      tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusWithUserMentionsToResolveTweet)
        cls.statusAdvertisingArticleTweet = cls.api.get_status(cls.statusAdvertisingArticle['id'],
                                                               tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusAdvertisingArticleTweet)
        cls.statusIsDifferentWithoutPictureTweet = cls.api.get_status(cls.statusNotAdvertisingArticleWithoutPicture['id'],
                                                                      tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusIsDifferentWithoutPictureTweet)
        cls.statusIsDifferentWithPictureTweet = cls.api.get_status(cls.statusNotAdvertisingArticleWithPicture['id'],
                                                                   tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusIsDifferentWithPictureTweet)
        cls.statusWithHashtagsInTextAndTextAndHashtagAfterLinkWithoutPhotoCreditsTweet = \
            cls.api.get_status(cls.statusWithHashtagsInTextAndTextAndHashtagAfterLinkWithoutPhotoCredits['id'],
                               tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusWithHashtagsInTextAndTextAndHashtagAfterLinkWithoutPhotoCreditsTweet)

        cls.statusWithTextAfterPhotoCreditsTweet = cls.api.get_status(cls.statusWithTextAfterPhotoCredits['id'], tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusWithTextAfterPhotoCreditsTweet)

        cls.statusWithTextAfterLinkAndWithoutPhotoCreditsTweet = cls.api.get_status(cls.statusWithTextAfterLinkAndWithoutPhotoCredits['id'], tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusWithTextAfterLinkAndWithoutPhotoCreditsTweet)

        cls.statusIsNormalTweet = cls.api.get_status(cls.statusIsNormal['id'], tweet_mode="extended")
        cls.allExampleTweets.append(cls.statusIsNormalTweet)


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
        self.assertFalse(main.getValidateTweet([self.statusWithCreditsURLsToResolveTweet], 600, 0))
        self.assertFalse(main.getValidateTweet([self.statusAdvertisingArticleTweet], 600, 0))
        self.assertFalse(
            main.getValidateTweet([self.statusIsDifferentWithoutPictureTweet, self.statusIsDifferentWithPictureTweet], 600, 0))
        self.assertFalse(main.getValidateTweet([self.statusIsNormalTweet], 999999, 99999))
        # hier sollte man die getNewestLuhzeTweets Function nochmal mocken, damit das mit den 999999 auch eine Liste mit Element produziert

    def test_craft_tweet_object_array(self):
        tweetObjectArray = main.craftTweetObjectArray(
            [self.statusWithCreditsURLsToResolveTweet, self.statusAdvertisingArticleTweet])
        self.assertIsInstance(tweetObjectArray, list)
        # check text
        self.assertEqual(self.statusWithCreditsURLsToResolve['text'], tweetObjectArray[0]['text'])
        self.assertEqual(self.statusAdvertisingArticle['text'], tweetObjectArray[1]['text'])
        # check link to picture
        self.assertEqual(self.statusWithCreditsURLsToResolve['pictureLink'], tweetObjectArray[0]['pictureLink'])
        self.assertEqual(self.statusAdvertisingArticle['pictureLink'], tweetObjectArray[1]['pictureLink'])
        # check link to article
        self.assertEqual(self.statusWithCreditsURLsToResolve['url'], tweetObjectArray[0]['linkToArticle'])
        self.assertEqual(self.statusAdvertisingArticle['url'], tweetObjectArray[1]['linkToArticle'])

    def test_resolve_urls(self):
        tweetObjectArray = main.craftTweetObjectArray(
            [self.statusWithCreditsURLsToResolveTweet, self.statusWithUserMentionsToResolveTweet])
        urlsResolvedArray = main.resolveUrls(tweetObjectArray)
        self.assertIsInstance(urlsResolvedArray, list)
        print(self.statusWithCreditsURLsToResolve['textAfterUrlsResolved'])
        print(urlsResolvedArray[0]['text'])
        self.assertEqual(self.statusWithCreditsURLsToResolve['textAfterUrlsResolved'], urlsResolvedArray[0]['text'])
        self.assertEqual(self.statusWithUserMentionsToResolve['textAfterUrlsResolved'], urlsResolvedArray[1]['text'])

    def test_resolve_user_mentions(self):
        tweetObjectArray = main.craftTweetObjectArray(
            [self.statusWithCreditsURLsToResolveTweet, self.statusWithUserMentionsToResolveTweet])
        userMentionsArray = main.resolveUserMentions(tweetObjectArray)
        self.assertIsInstance(userMentionsArray, list)
        self.assertEqual(self.statusWithCreditsURLsToResolve['text'], userMentionsArray[0]['text'])
        self.assertEqual(self.statusWithUserMentionsToResolve['textAfterUserMentionsResolved'], userMentionsArray[1]['text'])

    def test_resolve_hashtags(self):
        tweetObjectArray = main.craftTweetObjectArray(
            [self.statusWithCreditsURLsToResolveTweet, self.statusWithUserMentionsToResolveTweet, self.statusWithHashtagsInTextAndTextAndHashtagAfterLinkWithoutPhotoCreditsTweet])
        resolvedHashtagsArray = main.resolveHashtags(tweetObjectArray)
        self.assertEqual(self.statusWithCreditsURLsToResolve['text'], resolvedHashtagsArray[0]['text'])
        self.assertEqual(self.statusWithUserMentionsToResolve['text'], resolvedHashtagsArray[1]['text'])
        self.assertEqual(self.statusWithHashtagsInTextAndTextAndHashtagAfterLinkWithoutPhotoCredits['text'], resolvedHashtagsArray[2]['text'])

    def test_fetch_new_tweets(self):
        # kann sein, dass gerade ein artikel tweet hochgeladen wurde, dann schlägt der test fehl
        self.assertFalse(main.fetchNewTweets(600, 0, self.api))
        # kann sein das fehlschlägt wenn länger kein Artikel mehr kam
        self.assertTrue(main.fetchNewTweets(60000, 10, self.api))

    def test_send_tweet_to_telegram(self):
        self.assertEqual(0, main.sendTweetToTelegram(self.bot, [{"text": "test <a href=\"https://luhze.de\">test link</a>\n test text", "pictureLink": "https://pbs.twimg.com/media/ElRbFNCXEAQ4u6Q.jpg"}]))

    def test_check_if_link_is_in_feed(self):
        self.assertNotIn("https://www.luhze.de/2020/11/25/barriere-frei/", main.getLinksToLuhzeArticles())

    def test_all_example_tweets(self):
        validTweets = []
        for tweet in self.allExampleTweets:
            if (u"\u27A1" in tweet.full_text and "https://t.co/" in tweet.full_text and
                    True in [medium['type'] == 'photo' for medium in tweet.entities['media']] and
                    tweet.in_reply_to_status_id is None):
                validTweets.append(tweet)

        tweetObjectArray = main.craftTweetObjectArray(validTweets)
        resolvedUserMentionsArray = main.resolveUserMentions(tweetObjectArray)
        removedUrlArray = main.removeLinkToTweet(resolvedUserMentionsArray)
        replacedLinkArray = main.resolveUrls(removedUrlArray)
        resolvedHashtagsArray = main.resolveHashtags(replacedLinkArray)
        self.assertEqual(0, main.sendTweetToTelegram(self.bot, resolvedHashtagsArray))

    def test_main(self):
        self.assertEqual(0, main.main())


if __name__ == "__main__":
    unittest.main()
