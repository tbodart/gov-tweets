#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:00:57 2021

@author: teresabodart


This file collects data from twitter, and saves it to a csv file.  
It requires a file called `twitter_authentication.py` to be in this
user directory, and that file must contain:
    
    a tweepy `auth` object

This file writes a file called `tweets.csv`. 
Saving of this file is goverened by the Twitter developer license agreement.

"""

import tweepy, csv
# https://docs.tweepy.org/en/latest/api.html

from governor_dict import governors
# Source: https://twitter.com/i/lists/88692902/members (@TwitterGov)

from twitter_authentication import auth

# Connect to the Twitter API using the authentication
api = tweepy.API(auth)


def tweets_to_lists(search_terms_dict):

    def collect(search, num=100):
        """
        Perform a search on twitter, until a certain 
        number of tweets.
        """    
        tweet_list = []
        last_id = -1 # id of last tweet seen
        while len(tweet_list) < num:
            try:
                new_tweets = api.search(q=search, count=100, max_id=str(last_id - 1), tweet_mode="extended")
            except tweepy.TweepError as e:
                print("Error", e)
                break
            else:
                if not new_tweets:
                    #print("Could not find any more tweets!") commented out bc acceptable to have <100 per gov
                    break
                tweet_list.extend(new_tweets)
                last_id = new_tweets[-1].id

        return tweet_list
    
    governor_tweets = []
    
    for gov in list(search_terms_dict.values()):
        # Collect up to 100 tweets from each official governor's twitter account
        query = 'from:'+gov+'+-filter:retweets'
        tweet_list = collect(query)
        outtweets = [[tweet.id_str, tweet.created_at, tweet.user.screen_name, tweet.user.followers_count, tweet.user.created_at, tweet.user.verified, tweet.user.location, tweet.full_text, tweet.favorite_count, tweet.entities['hashtags']] for tweet in tweet_list]
        governor_tweets = governor_tweets + outtweets
    
    return governor_tweets

outtweets = tweets_to_lists(governors)


# write the csv - tweets.csv
with open('tweets.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "created_at", "username", "followers", "user_created_at", "verified", "location", "text", "likes", "hashtags"])
    writer.writerows(outtweets)
