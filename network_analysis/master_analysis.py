'''
Network Analysis Experiments - Master Dataset
COVID-19 Analysis | meganmp [at] bu [dot] edu
'''

# Imports
import csv
import emoji
import gzip
import json
import logging
import math
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import numpy as np
import os
import pandas as pd
import seaborn as sns
import unidecode
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats


# Import Google Client Library
#from google.cloud import language
# Import COVID-19 Data API
import COVID19Py

# NLTK Setup
#nltk.download('all')

# Access the Google NLP API
#CLIENT = language.LanguageServiceClient()
# Access the COVID19Py API
COVID = COVID19Py.COVID19(
    url='https://covid19-api.kamaropoulos.com')   # Mirror
# Define directories
root_dir = '/projectnb/caad/meganmp/data/COVID-19-TweetIDs-master' 
save_dir = '/projectnb/caad/meganmp/analysis/results/network_analysis/master'

# Pandas Settings
pd.set_option('max_colwidth', 280)  # Capture full tweet
pd.set_option("display.max_rows", None, "display.max_columns", None)

# Seaborn Settings
palette = sns.husl_palette(9, s=0.7)



def rank_entities(entity):
    ''' Return top 100 locations from location dictionary'''
    entity = OrderedDict(sorted(entity.items(), key=lambda x: x[1], reverse=True))
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
    interactions.add((str(row["in_reply_to_user_id"]), str(row["in_reply_to_screen_name"])))
    # Retweets
    interactions.add((str(row["retweeted_id"]), str(row["retweeted_screen_name"])))
    # User Mentions
    interactions.add((str(row["user_mention_id"]), str(row["user_mention_screen_name"])))
    
    # Discard user
    interactions.discard(row["user_id"])
    
    # Discard all None/NaN interactions
    interactions.discard(('None', 'None'))
    interactions.discard(('None', 'nan'))
    interactions.discard(('nan', 'None'))
    interactions.discard(('nan', 'nan'))

    return [row['user_id'], row['user_name']], interactions
            

def main():
    
    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'misinformation_hcq.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Misinformation Log of USA Dataset Tweets')
    
    # Initialize variables
    logging.info('Initialize dictionary')
    location_totals = dict()  
    
    # Read twitter objects into pandas dataframe
    for sub_dir, dirs, files in os.walk(root_dir):
            dirs.sort()
            files.sort()
            for date_dir in sorted(dirs):
                logging.info('Processing %s', date_dir)
                for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                    file_extension = os.path.splitext(file)[1]
                    if file_extension == '.gz':
                        logging.info('Processing %s', file)
                        with open(os.path.join(root_dir, date_dir, file), 'rb') as f:
                            gzip_f = gzip.GzipFile(fileobj=f)
                            try:
                                orig_df = pd.read_json(gzip_f, lines=True)
                            except:
                                continue
        
    # Drop extraneous information    
    orig_df = orig_df.drop('id_str', 1)
    orig_df = orig_df.drop('contributors', 1)
    orig_df = orig_df.drop('possibly_sensitive', 1)
    orig_df = orig_df.drop('lang', 1)
    orig_df = orig_df.drop('display_text_range', 1)
    orig_df = orig_df.drop('source', 1)
    orig_df = orig_df.drop('quoted_status_permalink',1)
    
    # Restructure dataframe
    tweet_df = pd.DataFrame(columns = ['created_at', 'id', 'user_id',
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
                                       'profile_loc'
                                       ])
    
    # Direct transfer of information
    transfer_cols = ['created_at', 'id', 'in_reply_to_status_id', 'in_reply_to_user_id',
                     'in_reply_to_screen_name']
    tweet_df[transfer_cols] = orig_df[transfer_cols]
    
    # Format remaining information
    tweet_df['hashtags'] = orig_df['entities'].apply(lambda x: [y['text'] for y in x['hashtags']])
    tweet_df['is_reply'] = orig_df['in_reply_to_screen_name'].apply(lambda x: False if x == None else True)
    tweet_df['is_retweet'] = orig_df['retweeted_status'].apply(lambda x: is_retweet(x))
    
    
    for index, row in orig_df.iterrows():
        
        # User ID
        if orig_df.loc[index, 'user']['id_str'] == None:
            tweet_df.loc[index, 'user_id'] = None
        else:
            tweet_df.loc[index, 'user_id'] = orig_df.loc[index, 'user']['id_str']
            tweet_df.loc[index, 'user_name'] = orig_df.loc[index, 'user']['screen_name']
            tweet_df.loc[index, 'user_followers_count'] = orig_df.loc[index, 'user']['followers_count']
        
        # User Mentions
        if not orig_df.loc[index, 'entities']['user_mentions']:
            tweet_df.loc[index, 'has_mentions'] = False
        else:
            tweet_df.loc[index, 'has_mentions'] = True
            tweet_df.loc[index, 'user_mention_id'] = orig_df.loc[index, 'entities']['user_mentions'][0]['id']
            tweet_df.loc[index, 'user_mention_screen_name'] = orig_df.loc[index, 'entities']['user_mentions'][0]['screen_name']
        
        # Capture full text of tweet
        if is_retweet(orig_df.loc[index, 'retweeted_status']):
            tweet_df.loc[index, 'tweet_text'] = preprocess_retweet(row['retweeted_status'])
            tweet_df.loc[index, 'retweeted_id'] = orig_df.loc[index, 'retweeted_status']['user']['id_str']
            tweet_df.loc[index, 'retweeted_screen_name'] = orig_df.loc[index, 'retweeted_status']['user']['screen_name']
        else:
            try:
                tweet_df.loc[index, 'tweet_text'] = preprocess_ext_tweet(row['extended_tweet'])
            except:
                tweet_df.loc[index, 'tweet_text'] =  row['full_text']
                
        # Geotagging
        if orig_df.loc[index, 'geo'] == None:
            tweet_df.loc[index, 'is_geo'] = False
            tweet_df.loc[index, 'geo_coordinates'] = None
        else:
            try:
                tweet_df.loc[index, 'geo_coordinates'] = orig_df.loc[index, 'geo']['coordinates']
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
            tweet_df.loc[index, 'profile_loc'] = orig_df.loc[index, 'user']['location']
                
    logging.info('ORGANIZING DATA COMPLETE')
    
    # Save pkl file
    tweet_df.to_pickle('usa_tweets_df.pkl')
    
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
    subnetwork = network.subgraph(max(nx.connected_components(network), key=len))
    
    # Calculate degrees of each node
    degrees = [deg for (node, deg) in network.degree()]
    sub_degrees = [deg for (node, deg) in subnetwork.degree()]
            
    with open('network_analysis-expanded.txt', 'w') as file_out:
        file_out.write('Nodes = {}\n'.format(network.number_of_nodes()))
        file_out.write('Edges = {}\n'.format(network.number_of_edges()))
        file_out.write('Max Degree = {}\n'.format(np.max(degrees)))
        file_out.write('Average degree = {}\n'.format(np.mean(degrees)))
        file_out.write('Most frequent degree = {}\n'.format(stats.mode(degrees)[0][0]))
        file_out.write('# Connected Components = {}\n'.format(nx.number_connected_components(network)))
    
        if nx.is_connected(network):
            file_out.write('Network is connected.\n')
        else:
            file_out.write('Network not connected.\n')
        
        file_out.write('\nLargest Subgraph Analysis\n')
        file_out.write('Nodes = {}\n'.format(subnetwork.number_of_nodes()))
        file_out.write('Edges = {}\n'.format(subnetwork.number_of_edges()))
        file_out.write('Max Degree = {}\n'.format(np.max(sub_degrees)))
        file_out.write('Average degree = {}\n'.format(np.mean(sub_degrees)))
        file_out.write('Most frequent degree = {}\n'.format(stats.mode(sub_degrees)[0][0]))
        file_out.write('# Connected Components = {}\n'.format(nx.number_connected_components(subnetwork)))
        
    degree_dict = dict(network.degree())
    most_connected_user = max(dict(network.degree()).items(), key = lambda x: x[1])

    plt.figure(figsize=(50,50))
    nx.draw(network)
    plt.savefig('network-usa.jpg')
    
    plt.figure(figsize=(50,50))
    nx.draw(subnetwork)
    plt.savefig('subnetwork-usa.jpg')
        
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
            
