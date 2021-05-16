'''
Hydroxychloroquine Tweets: Analyze Keywords and Timeline
COVID-19 Analysis | meganmp@bu.edu
'''

# -*- coding: utf-8 -*-


# Imports
import csv
import emoji
import errno
import gzip
import json
import logging
import math
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import nltk
import numpy as np
import os
import pandas as pd
import pickle as pkl
import re
import seaborn as sns
import sys
import time
import unidecode
from datetime import datetime
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pandas.plotting import register_matplotlib_converters
from scipy import stats

# Import Google Client Library
from google.cloud import language
# Import COVID-19 Data API
import COVID19Py

# NLTK Setup
nltk.download('all')

# Access the Google NLP API
CLIENT = language.LanguageServiceClient()
# Access the COVID19Py API
COVID = COVID19Py.COVID19(
    url='https://covid19-api.kamaropoulos.com')   # Mirror


# Define directories
root_dir = '/projectnb/caad/meganmp/data/misinformation/'
save_dir = '/projectnb/caad/meganmp/analysis/results/misinformation/keywords'

# Pandas Settings
pd.set_option('max_colwidth', 280)  # Capture full tweet
pd.set_option("display.max_rows", None, "display.max_columns", None)

# Seaborn Settings
palette = sns.husl_palette(9, s=0.7)


def rank_entities(entity):
    ''' Return top 100 locations from location dictionary'''
    entity = OrderedDict(
        sorted(entity.items(), key=lambda x: x[1], reverse=True))
    first_n_values = list(entity.items())[:100]
    return first_n_values


def preprocess_location(loc):
    # Remove emoji
    try:
        loc = remove_emoji(loc)
    except:
        pass
    # Lowercase
    loc = loc.lower()
    # Replace accented characters
    try:
        loc = unidecode.unidecode(loc)
    except:
        pass
    # Remove extraneous whitespace
    loc = loc.strip()
    return loc


def preprocess_retweet(rt):
    ''' Return full text of cleaned up tweet '''
    try:
        tweet = rt['text']
    except KeyError:
        tweet = rt['full_text']
    return tweet


def preprocess_ext_tweet(ext_tweet):
    tweet = ext_tweet['full_text']
    return tweet


def is_retweet(x):
    try:
        if math.isnan(x):
            return False
    except:
        return True


def get_interactions(row):
    '''Build Interactions for Network'''

    # Define interactions
    interactions = set()

    # Replies
    interactions.add((str(row["in_reply_to_user_id"]),
                     str(row["in_reply_to_screen_name"])))
    # Retweets
    interactions.add(
        (str(row["retweeted_id"]), str(row["retweeted_screen_name"])))
    # User Mentions
    interactions.add((str(row["user_mention_id"]),
                     str(row["user_mention_screen_name"])))

    # Discard user
    interactions.discard(row["user_id"])

    # Discard all None/NaN interactions
    interactions.discard(('None', 'None'))
    interactions.discard(('None', 'nan'))
    interactions.discard(('nan', 'None'))
    interactions.discard(('nan', 'nan'))

    return [row['user_id'], row['user_name']], interactions


def preprocess_tweet(tweet):
    ''' Return full text of cleaned up tweet '''
    if 'retweeted_status' in tweet.keys():   # Check if retweet
        try:
            tweet = tweet['retweeted_status']['text']
        except KeyError:
            tweet = tweet['retweeted_status']['full_text']
    else:
        try:
            tweet = tweet['extended_tweet']['full_text']
        except KeyError:
            tweet = tweet['full_text']

    # Clean Tweet
    tweet = clean_tweet(tweet)

    return tweet


def clean_tweet(tweet):
    ''' Return cleaned up Tweet for Sentiment Analysis'''
    # Lowercase
    tweet = tweet.lower()

    # Remove URLs
    tweet = re.sub(r'https?:\/\/\S+', '', tweet)
    tweet = re.sub(r'www.[\S]+', '', tweet)

    # Remove usernames
    tweet = re.sub(r'@[\S_]+', '', tweet)

    # Remove '#' symbol in hashtags
    tweet = re.sub('#', '', tweet)

    # Remove extraneous whitespace
    tweet = re.sub('[\t\n\r\f\v]', '', tweet)

    # Remove emoji
    tweet = remove_emoji(tweet)

    # Tokenize tweet
    tweet = nltk.word_tokenize(tweet)

    # Remove stopwords
    stopwords = set(nltk.corpus.stopwords.words("english"))
    tweet = remove_stopwords(tweet, stopwords)

    # Identify parts of speech
    tweet = nltk.pos_tag(tweet)

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tweet = lemmatize_tweet(tweet, lemmatizer)

    # Reconstitute tweet
    tweet = ' '.join(tweet)

    return tweet


def remove_emoji(tweet):
    return emoji.get_emoji_regexp().sub(r'', tweet)


def remove_stopwords(tweet, stopwords):
    filtered_tweet = []
    for word in tweet:
        if word not in stopwords:
            filtered_tweet.append(word)
    return filtered_tweet


def lemmatize_tweet(tweet, lemmatizer):
    lemma_tweet = [lemmatizer.lemmatize(word[0], pos=(
        get_wordnet_pos(word[1]))) for word in tweet]
    return lemma_tweet


def get_wordnet_pos(treebank_tag):
    '''Conversion from https://bit.ly/3vQ49de'''
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    else:
        return wn.NOUN


def sentiment_analysis(tweet):
    ''' Sentiment analysis on input '''
    document = language.Document(
        content=tweet,
        type_=language.Document.Type.PLAIN_TEXT,
    )

    response = CLIENT.analyze_sentiment(
        document=document,
        encoding_type='UTF32',
    )

    sentiment = response.document_sentiment

    return sentiment


def evaluate(score, mag):
    ''' Sentiment analysis thresholding and interpretation '''
    # Strongly Positive
    if score > 0.2 and mag > 2.0:
        return '++'
    # Weakly Positive
    if score > 0.2 and mag < 2.0:
        return '+'
    # Neutral
    if -0.2 <= score <= 0.2 and mag < 2.0:
        return ' '
    # Mixed
    if -0.2 <= score <= 0.2 and mag > 2.0:
        return 'Mixed'
    # Weakly Negative
    if score < -0.2 and mag < 2.0:
        return '-'
    # Strongly Negative
    return '--'


def node_color(interp):
    if interp == '++':
        return 'g'
    if interp == '+':
        return 'g'
    if interp == 'Mixed':
        return 'y'
    if interp == '-':
        return 'r'
    if interp == '--':
        return 'r'
    else:
        return 'w'


def main():

    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'misinformation_hcq.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Misinformation Log of USA Dataset HCQ Tweets')

    # Initialize variables
    logging.info('Initialize dictionary')
    location_totals = dict()

    # Read twitter objects into pandas dataframe
    with open(os.path.join(root_dir, 'hcq-tweets.jsonl.gz'), 'rb') as f:
        gzip_f = gzip.GzipFile(fileobj=f)
        orig_df = pd.read_json(gzip_f, lines=True)

    # Drop extraneous information
    orig_df = orig_df.drop('id_str', 1)
    orig_df = orig_df.drop('contributors', 1)
    orig_df = orig_df.drop('possibly_sensitive', 1)
    orig_df = orig_df.drop('lang', 1)
    orig_df = orig_df.drop('display_text_range', 1)
    orig_df = orig_df.drop('source', 1)
    orig_df = orig_df.drop('quoted_status_permalink', 1)

    # Restructure dataframe
    tweet_df = pd.DataFrame(columns=['created_at', 'id', 'user_id',
                                      'tweet_text', 'hashtags',
                                      'user_followers_count',
                                      'is_reply',
                                      'in_reply_to_status_id',
                                      'in_reply_to_user_id',
                                      'in_reply_to_screen_name',
                                      'is_retweet',
                                      'retweeted_id',
                                      'retweeted_screen_name',
                                      'has_mentions',
                                      'user_mention_id',
                                      'user_mention_screen_name',
                                      'is_geo',
                                      'geo_coordinates',
                                      'is_profile_loc',
                                      'profile_loc',
                                      'sentiment',
                                      'sentiment_score',
                                      'sentiment_mag',
                                      'interpretation',
                                      'node_color'
                                      ])

    # Direct transfer of information
    transfer_cols = ['created_at', 'id', 'in_reply_to_status_id', 'in_reply_to_user_id',
                      'in_reply_to_screen_name']
    tweet_df[transfer_cols] = orig_df[transfer_cols]

    # Format remaining information
    tweet_df['hashtags'] = orig_df['entities'].apply(
        lambda x: [y['text'] for y in x['hashtags']])
    tweet_df['is_reply'] = orig_df['in_reply_to_screen_name'].apply(
        lambda x: False if x == None else True)
    tweet_df['is_retweet'] = orig_df['retweeted_status'].apply(
        lambda x: is_retweet(x))

    for index, row in orig_df.iterrows():

        # User ID
        if orig_df.loc[index, 'user']['id_str'] == None:
            tweet_df.loc[index, 'user_id'] = None
        else:
            tweet_df.loc[index, 'user_id'] = orig_df.loc[index,
                                                          'user']['id_str']
            tweet_df.loc[index, 'user_name'] = orig_df.loc[index,
                                                            'user']['screen_name']
            tweet_df.loc[index, 'user_followers_count'] = orig_df.loc[index,
                                                                      'user']['followers_count']

        # User Mentions
        if not orig_df.loc[index, 'entities']['user_mentions']:
            tweet_df.loc[index, 'has_mentions'] = False
        else:
            tweet_df.loc[index, 'has_mentions'] = True
            tweet_df.loc[index, 'user_mention_id'] = orig_df.loc[index,
                                                                  'entities']['user_mentions'][0]['id']
            tweet_df.loc[index, 'user_mention_screen_name'] = orig_df.loc[index,
                                                                          'entities']['user_mentions'][0]['screen_name']

        # Capture full text of tweet
        if is_retweet(orig_df.loc[index, 'retweeted_status']):
            tweet_df.loc[index, 'tweet_text'] = preprocess_retweet(
                row['retweeted_status'])
            tweet_df.loc[index, 'retweeted_id'] = orig_df.loc[index,
                                                              'retweeted_status']['user']['id_str']
            tweet_df.loc[index, 'retweeted_screen_name'] = orig_df.loc[index,
                                                                        'retweeted_status']['user']['screen_name']
        else:
            try:
                tweet_df.loc[index, 'tweet_text'] = preprocess_ext_tweet(
                    row['extended_tweet'])
            except:
                tweet_df.loc[index, 'tweet_text'] = row['full_text']

        # Geotagging
        if orig_df.loc[index, 'geo'] == None:
            tweet_df.loc[index, 'is_geo'] = False
            tweet_df.loc[index, 'geo_coordinates'] = None
        else:
            try:
                tweet_df.loc[index, 'geo_coordinates'] = orig_df.loc[index,
                                                                      'geo']['coordinates']
                tweet_df.loc[index, 'is_geo'] = True
            except:
                tweet_df.loc[index, 'is_geo'] = False
                tweet_df.loc[index, 'geo_coordinates'] = None

        # User Location
        if orig_df.loc[index, 'user']['location'] == None or type(orig_df.loc[index, 'user']['location']) != str:
            tweet_df.loc[index, 'is_profile_loc'] = False
            tweet_df.loc[index, 'profile_loc'] = None
        else:
            tweet_df.loc[index, 'is_profile_loc'] = True
            tweet_df.loc[index, 'profile_loc'] = orig_df.loc[index,
                                                              'user']['location']

        
    logging.info('ORGANIZING DATA COMPLETE')

    # Save pkl file
    tweet_df.to_pickle('hcq_tweets_df.pkl')
    # # Load pkl file
    #tweet_df = pd.read_pickle('hcq_tweets_df.pkl')

    # Build Network Graph
    network = nx.Graph()

    for index, row in tweet_df.iterrows():
        user, interactions = get_interactions(row)
        user_id = user[0]
        user_name = user[1]
        tweet_id = row["id"]
        for interaction in interactions:
            int_id, int_name = interaction
            network.add_edge(user_id, int_id, tweet_id=tweet_id)
            network.nodes[user_id]["name"] = user_name
            network.nodes[int_id]["name"] = int_name

   

    # Identify largest subnetwork
    subnetwork = network.subgraph(
        max(nx.connected_components(network), key=len))

    # Calculate degrees of each node
    degrees = [deg for (node, deg) in network.degree()]
    sub_degrees = [deg for (node, deg) in subnetwork.degree()]

    with open('network_analysis.txt', 'w') as file_out:
        file_out.write('Nodes = {}\n'.format(network.number_of_nodes()))
        file_out.write('Edges = {}\n'.format(network.number_of_edges()))
        file_out.write('Max Degree = {}\n'.format(np.max(degrees)))
        file_out.write('Average degree = {}\n'.format(np.mean(degrees)))
        file_out.write('Most frequent degree = {}\n'.format(
            stats.mode(degrees)[0][0]))
        file_out.write('# Connected Components = {}\n'.format(
            nx.number_connected_components(network)))

        if nx.is_connected(network):
            file_out.write('Network is connected.\n')
        else:
            file_out.write('Network not connected.\n')

        file_out.write('Largest Subgraph Analysis')
        file_out.write('Nodes = {}\n'.format(subnetwork.number_of_nodes()))
        file_out.write('Edges = {}\n'.format(subnetwork.number_of_edges()))
        file_out.write('Max Degree = {}\n'.format(np.max(sub_degrees)))
        file_out.write('Average degree = {}\n'.format(np.mean(sub_degrees)))
        file_out.write('Most frequent degree = {}\n'.format(
            stats.mode(sub_degrees)[0][0]))
        file_out.write('# Connected Components = {}\n'.format(
            nx.number_connected_components(subnetwork)))

    degree_dict = dict(network.degree())
    most_connected_user = max(dict(network.degree()).items(), key=lambda x: x[1])
    
    # Sentiment Analysis on 50 most highly interconnected nodes
    tweet_df['tweet_clean'] = tweet_df['tweet_text'].apply(lambda x: clean_tweet(x))
    
    for index, row in tweet_df.iterrows():
        tweet_df.loc[index, 'node_color'] = 'k'
        #if tweet_df.loc[index, 'user_id'] in 
        sentiment = sentiment_analysis(tweet_df.loc[index, 'tweet_clean'])
        tweet_df.loc[index, 'sentiment_score'] = [sentiment.score]
        tweet_df.loc[index, 'sentiment_mag'] = [sentiment.magnitude]
        tweet_df.loc[index, 'interpretation'] = evaluate(tweet_df.loc[index, 'sentiment_score'], tweet_df.loc[index, 'sentiment_mag'])
        tweet_df.loc[index, 'node_color'] = node_color(tweet_df.loc[index, 'interpretation'])
        time.sleep(.15)
    
    # Node Color Map
    node_colors = []
    for node in network:
        node_colors.append()

    plt.figure(figsize=(50, 50))
    nx.draw(network)
    plt.savefig('network.jpg')

    plt.figure(figsize=(50, 50))
    nx.draw(subnetwork)
    plt.savefig('subnetwork.jpg')

    ##########################################################################
    # Hashtag Count Relative to Retweet Status
    # plt.figure(figsize=(24,16))
    # sns.set(font_scale=2)
    # hashable_df = tweet_df.explode('hashtags')
    # hashable_df = hashable_df[hashable_df['hashtags'] != 'hydroxychloroquine']
    # hashtag_count = sns.countplot(data=hashable_df,
    #                               y = 'hashtags',
    #                               hue = 'is_retweet',
    #                               order=pd.value_counts(hashable_df['hashtags']).iloc[1:10].index).set(title='Most Common Hashtags on Hydroxychloroquine Tweets')
    # plt.savefig('HCQ_hashtag_count_cf_RT_status.jpg')

    # Keyword Frequency Plot
    # hcq_keywords = pd.Series(sum([item for item in tweet_df.hashtags], [])).value_counts()
    # hashtag_df = hcq_keywords.to_frame()
    # hashtag_df = hashtag_df.reset_index()
    # hashtag_df.columns = ['hashtag','frequency']
    # plt.figure(figsize=(30,25))
    # sns.set(font_scale = 3.5)
    # plt.xticks(rotation=30)
    # keyword_freq_plot = sns.barplot(data=hashtag_df[1:10], x = 'hashtag',
    #                                 y= 'frequency').set(title='Most Frequently Used Hashtags in Hydroxychloroquine Dataset',
    #                                                     xlabel='Hashtag',
    #                                                     ylabel='Count')
    # plt.savefig('HCQ_hashtag_frequency.png')
    # plt.savefig('HCQ_hashtag_frequency.jpg')

    # Plot coordinates of Tweet origin
    # There are none reported.

    # Tweet Hashtag Over Time
    # Tweets per time bin (every 4 hours)
    # sns.set(font_scale=2)
    # HCQ_bin_df = tweet_df.groupby(pd.Grouper(key='created_at', freq='4H', convention='start')).size()
    # plt.figure(figsize=(30,25))
    # ex = sns.lineplot(data=HCQ_bin_df).set(ylabel='Tweet Count', xlabel='Date (4H Time Bin)',
    #                                        title='#hydroxychloroquine Tweets per 4H Time Bin (May-June 2020)')
    # plt.grid(True)
    # plt.savefig('Hashtag_HCQ_Tweets_Over_Time.jpg')

    # # Rank top 100 locations
    # logging.info('Ranking top 100 locations')
    # top100locs = rank_entites(location_totals)

    # # Save top 100 locations in csv
    # logging.info('Saving top 100 locations csv')
    # with open(os.path.join(save_dir, 'top100locations-hcq.csv'), 'w') as f3:
    #     write = csv.writer(f3)
    #     write.writerow(top100locs)

    # # Save location totals dictionary
    # logging.info('Saving location totals')
    # with open(os.path.join(save_dir, 'location_totals-hcq.json'), 'w') as f4:
    #     json.dump(location_totals, f4)

    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
