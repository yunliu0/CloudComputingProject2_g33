"""
# Project           : Gig Economy and its impact in Australia
# Team              : Group 33
# City              : Melbourne, Australia
# Authors           : Qing Feng Chye 770376, Sii Kim Lau 890511, Rohan Jahagirdar 835450
#                     Yun Liu 1046589, Shorye Chopra 689913
# Purpose           : Twitter Harvester logic
"""
import tweepy
import json
import re
import couchdb_requests
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import ssl


# disable ssl checking
# Reference from https://stackoverflow.com/questions/38916452/nltk-download-ssl-certificate-verify-failed
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')


# Tweepy
# SEARCH API
# Search result based on query given, giving tweets, check tweets condition
def mainFunction(api, query, all_keywords, count, language, region, couch_vars):

    totalExplored = 0
    totalUsefulTweets = 0
    friendsIdList = []
    for keyword in query:
        print("Key word currently being searched: %s" % keyword)
        lastId = None
        tweets = True

        while (tweets):
            tweets = api.search(q=[keyword], count=count,
                                lang=language, max_id=lastId)

            if tweets:
                for tweet in tweets:
                    tweet_json = tweet._json

                    totalExplored += 1
                    single_result = CheckTwitter(tweet_json, keyword, region)
                    # We only interested the tweets in Australia and keyword in text
                    if single_result != False:
                        totalUsefulTweets += 1
                        # Tweets storing process here
                        valid = couchdb_requests.couch_post(
                            couch_vars, single_result)
                        if valid:
                            print(
                                "==================================GET FRIENDS ID================================================================")
                            # Finding Friends of friends section
                            user = tweet_json['user']
                            user_id = user['id']
                            if len(friendsIdList) < 100000000:
                                friendsIdList += searchFriends(api, user_id)

                    print("Total Explored: %d" % totalExplored)
                    print("Total Useful Tweets: %d" % totalUsefulTweets)

                lastId = tweets[-1]._json['id'] - 1

    if len(friendsIdList) > 0:
        print("===================================Finding friends tweets start here================================================")
        print("Num of friends: %d" % len(friendsIdList))
        totalExplored, totalUsefulTweets = ProcessRelatedTweets(
            api, friendsIdList, all_keywords, region, totalExplored, totalUsefulTweets, couch_vars, [])

    return


# Get a list of follower ids for the target account, input take in user id, output friend's ID as a list
def searchFriends(api, target):

    friendsIDList = api.friends_ids(target, cursor=-1)[0]

    return friendsIDList


# Finding friends' timeline tweets, also check if the tweets is useful, and record accordingly
def ProcessRelatedTweets(api, friendsIdList, all_keywords, region, totalExplored, totalUsefulTweets, couch_vars, friendsoffriends):
    if len(friendsIdList) > 0:

        for Id in friendsIdList:

            try:
                # Searching tweets from timeline of user
                tweets = api.user_timeline(user_id=Id, count=500, lang='en')

                for tweet in tweets:
                    totalExplored += 1

                    tweet_json = tweet._json
                    single_result = CheckFriendsTwitter(
                        tweet_json, all_keywords, region)

                    if single_result != False:
                        valid = couchdb_requests.couch_post(
                            couch_vars, single_result)
                        totalUsefulTweets += 1

                        if valid:
                            print(
                                "==================================GET FRIENDS OF FRIENDS ID===========================================================")
                            # Finding Friends of friends section
                            user = tweet_json['user']
                            user_id = user['id']
                            if len(friendsoffriends) < 100000000:
                                friendsoffriends += searchFriends(api, user_id)

            except Exception:  # Might because the user is private, so need to catch the exception.
                print(Exception)
                pass

        return ProcessRelatedTweets(api, friendsoffriends,  all_keywords, region, totalExplored, totalUsefulTweets, couch_vars, [])
    else:
        return (totalExplored, totalUsefulTweets)


# filter tweets: only the one match region with the keyword
def CheckTwitter(tweet, keyword, region):

    loc = getLocation(tweet)
    text = tweet['text']

    if (loc in region) and (not isRetweet(text)):
        if (isUseful(keyword, text)):
            extracted_result = extractTweetImpAttr(tweet, loc, keyword, text)

            return extracted_result

    return False


# As going into friend's list, need to check all keywords
def CheckFriendsTwitter(tweet, all_keywords, region):

    loc = getLocation(tweet)
    text = tweet['text']

    if (loc in region) and (not isRetweet(text)):
        for keyword in all_keywords:
            if (isUseful(keyword, text)):
                extracted_result = extractTweetImpAttr(
                    tweet, loc, keyword, text)

                return extracted_result

    return False


# Extract tweets with just the id, created date, text
# location, matched keyword and sentimental value
def extractTweetImpAttr(tweet, loc, keyword, text):
    reqTweetAttr = {}
    reqTweetAttr['_id'] = json.dumps(tweet['id'])
    reqTweetAttr['created_at'] = tweet['created_at']
    reqTweetAttr['text'] = text
    reqTweetAttr['location'] = loc
    reqTweetAttr['keyword'] = keyword

    # get the sentiment value of the tweet
    tweetTextBlob = TextBlob(text)
    analyzer = SentimentIntensityAnalyzer()
    totalSentimentValue = 0
    numSentences = 0
    for sentence in tweetTextBlob.sentences:
        vs = analyzer.polarity_scores(sentence)
        totalSentimentValue += vs['compound']
        numSentences += 1

    reqTweetAttr['sentimental'] = totalSentimentValue/numSentences

    return reqTweetAttr


# get the location of the tweet based on the place of the tweet
# or the user location
def getLocation(tweet):
    loc = None
    place = None

    try:
        place = tweet['place']
    except Exception:
        pass

    if place != None:
        if place['country_code'] == 'AU':
            if place['full_name'] != None:
                loc = place['full_name'].split(',')[0]
    else:
        try:
            user = tweet['user']
            location = user['location']
            if location != None:
                loc = location.split(',')[0]
        except Exception:
            pass

    return loc


# check if the tweet is useful for our analysis
# does not take retweets
def isUseful(keyword, text):
    if (re.search(r'\b{}'.format(keyword), text, flags=re.IGNORECASE)):
        return True

    return False


# check if the tweet is a retweet
def isRetweet(text):
    if (re.search(r'\bRT @', text)):
        return True

    return False
