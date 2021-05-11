#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 17:14:16 2021

@author: teresabodart

This file reads tweet data from a csv, processes it, and produces a new
pandas dataframe
 
It requires a file called 'tweets.csv' to be in the current directory.

This file writes a file called `part3_processed_data.csv`. 

"""

import pandas as pd
import json
import csv
from datetime import datetime

gov_tweets = pd.read_csv('tweets.csv')

## Cleaning hashtag column ##
def clean_hashtag(string_of_list):
    '''
    Hashtags did not transfer cleanly, filtering for just the text
    Input is a string of a list of dictionaries, with keys 'text' and 'indices'
    '''
    import ast
    # Using ast (Abstract Syntax Trees) to convert string to list
    a_list = ast.literal_eval(string_of_list)
    
    hashtags = [dict_['text'] for dict_ in a_list]
    return hashtags

gov_tweets['hashtags'] = gov_tweets['hashtags'].apply(clean_hashtag)

## Converting created_at to datetime format ##
gov_tweets['created_at'] = pd.to_datetime(gov_tweets['created_at'])

def avg_likes_per_gov(df):
    '''
    Returns dictionary of average likes per tweet for each governor
    '''
    grouped = df.groupby("username")
    return grouped.apply(lambda x: x.likes.mean()).to_dict()

def covid_mentions(df):
    '''
    Returns three dicts of total, avg, and proportional mentions of 'covid',  
    'vaccine/vaccination', and 'pandemic' per tweet by each governor
    '''
    lowercase = lambda t: t.lower()
    count_mentions = lambda t: t.count('covid') + t.count('vaccin') + t.count('pandemic')
    check_mentions = lambda t: True if (t.count('covid') + t.count('vaccin') + t.count('pandemic')) > 0 else False
    
    # Create series of covid/vaccine/pandemic mentions per tweet, and series if mentioned T/F
    df['count_series'] = gov_tweets.text.apply(lowercase).apply(count_mentions) # count column
    df['mentioned_covid'] = df.text.apply(lowercase).apply(check_mentions) #T/F column
    
    # Group by governor and get sum, mean, and proportion of tweets mentioning COVID
    grouped = df.groupby("username")
    total_mentions = grouped.apply(lambda x: x.count_series.sum()).to_dict()
    avg_mentions = grouped.apply(lambda x: x.count_series.mean()).to_dict()
    proportion_incl_covid = grouped.apply(lambda x: x.mentioned_covid.mean()).to_dict()
    
    return total_mentions, avg_mentions, proportion_incl_covid

def common_companion_hashtags(df):
    '''
    Returns dictionary of most common hashtag for each governor 
    '''
    def most_frequent(a_list):
        return max(set(a_list), key=a_list.count, default='')
    
    make_lower = lambda x: [w.lower() for w in x]
    
    def most_common_hashtag(df):
        '''
        Input is a dataframe containing lists of hashtags
        Output is string of the most common hashtag
        '''
        # Make all lowercase
        lowers = df.hashtags.apply(make_lower)
        hashtags = lowers.str.join(' ')
        # Join all words from series of lists
        all_hashtags = ' '.join(hashtags)
        hashtag_list = all_hashtags.split()
        
        return most_frequent(hashtag_list)
    grouped = df.groupby('username')
    
    return grouped.apply(most_common_hashtag).to_dict()

def get_user_created_at(df):
    '''
    Returns dictionary of account created date for each governor
    '''
    grouped = df.groupby('username')
    return grouped.user_created_at.first().to_dict()

def get_user_location(df):
    from governor_dict import governors
    '''
    Returns dictionary of account created date for each governor
    Using dictionary 'governors' I created to simplify process, just reverse dict
    '''
    # GeoDataFrame to join with has capitalized states, updating here
    inv_dict = {v: k.upper() for k, v in governors.items()}
    
    return inv_dict

def get_user_followers(df):
    '''
    Returns dictionary of account created date for each governor
    '''
    grouped = df.groupby('username')
    return grouped.followers.first().to_dict()

## Create dataframe, add year_created column ##

# `covid_mentions()` returns 3 dicts, separate here to go into list of dicts nicely
total_covid_mentions, average_covid_mentions, proportion_includes_covid = covid_mentions(gov_tweets)

headers = ['username', 'average_likes', 'total_covid_mentions', 'average_covid_mentions', 
           'proportion_includes_covid', 'most_common_hashtag', 'user_created_at', 'location', 'followers']
# Dictionary to DataFrame created df with username as columns, need to transpose, reset index, and rename columns
processed_df = pd.DataFrame.from_dict([avg_likes_per_gov(gov_tweets), 
                                       total_covid_mentions, 
                                       average_covid_mentions, 
                                       proportion_includes_covid,
                                       common_companion_hashtags(gov_tweets),
                                       get_user_created_at(gov_tweets),
                                       get_user_location(gov_tweets),
                                       get_user_followers(gov_tweets)]).transpose().reset_index()
# Add correct column names to transposed DataFrame
processed_df.columns = headers
# Make into datetime objects
processed_df.user_created_at = pd.to_datetime(processed_df.user_created_at)
# Make "year account created" column
get_year = lambda x: x.year
processed_df['year_created'] = processed_df.user_created_at.apply(get_year)

# Write processed data to csv
processed_df.to_csv(path_or_buf='part3_processed_data.csv', mode='w', header=True, index=False)
