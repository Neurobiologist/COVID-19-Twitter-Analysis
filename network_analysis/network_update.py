# Imports
import emoji
import matplotlib.pyplot as plt
import networkx as nx
import nltk
import numpy as np
import pandas as pd
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from scipy import stats

# Pandas Settings
pd.set_option('max_colwidth', 280)  # Capture full tweet
pd.set_option("display.max_rows", None, "display.max_columns", None)

# NLTK Settings
nltk.download('all')
sia = SentimentIntensityAnalyzer()

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

    return [str(row['user_id']), str(row['user_name'])], interactions

def preprocess_tweet(tweet):
    ''' Return full text of cleaned up tweet '''
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
    lemma_tweet = [lemmatizer.lemmatize(word[0], pos=(get_wordnet_pos(word[1]))) for word in tweet]
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
    sentiment = sia.polarity_scores(tweet)['compound']

    return sentiment


def evaluate(score):
    ''' Sentiment analysis thresholding and interpretation '''
    # Strongly Positive
    if score > 0.25:
        return '++'
    # Weakly Positive
    elif 0.05 < score <= 0.25:
        return '+'
    # Neutral
    elif -0.05 <= score <= 0.05:
        return ' '
    # Weakly Negative
    elif -.025 <= score < -0.05:
        return '-'
    # Strongly Negative
    if score < -0.25:
        return '--'


def mkr(interp):
    ''' Assign marker based on interpretation '''
    if interp == '++':
        return 'blue'
    if interp == '+':
        return 'teal'
    if interp == ' ':
        return 'moccasin'
    if interp == '-':
        return 'mistyrose'
    return 'red'


def tweet_polarity(tweet_data):
    ''' Plot histogram of tweet data '''
    plt.hist(tweet_data['Sentiment_Score'], bins='auto')
    plt.title(
        'COVID-19 Sentiment Distribution for @{}'.format(tweet_data['ID'][0]))
    plt.xlabel('Sentiment Score')
    plt.xlim(-1, 1)
    plt.show()
    # plt.savefig('tweet_data.png')
    
def build_network(network, tweet_df):
    ''' Build network node by node'''
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

def colorize_network(network, tweet_df, colors, blank_nodes):
    ''' Add color to nodes based on sentiment'''
    for node in network:
        # User ID
        if (node in tweet_df['user_id'].values) or (int(float(node)) in tweet_df['user_id'].values):
            if tweet_df.index[tweet_df['user_id'] == node].empty:
                blank_nodes.append(node)
            else:
                colors.append((tweet_df.loc[tweet_df['user_id'] == node]['marker_color']).values[0])
        # User Mention ID
        elif (node in tweet_df['user_mention_id'].values) or (int(float(node)) in tweet_df['user_mention_id'].values):
            if tweet_df.index[tweet_df['user_mention_id'] == node].empty:
                blank_nodes.append(node)
            else:
                colors.append((tweet_df.loc[tweet_df['user_mention_id'] == node]['marker_color']).values[0])
        # Retweet
        elif (node in tweet_df['retweeted_id'].values) or (int(float(node)) in tweet_df['retweeted_id'].values):
            if tweet_df.index[tweet_df['retweeted_id'] == node].empty:
                blank_nodes.append(node)
            else:
                colors.append((tweet_df.loc[tweet_df['retweeted_id'] == node]['marker_color']).values[0])
        # Reply
        elif (node in tweet_df['in_reply_to_user_id'].values) or (int(float(node)) in tweet_df['in_reply_to_user_id'].values):
            if tweet_df.index[tweet_df['in_reply_to_user_id'] == node].empty:
                blank_nodes.append(node)
            else:
                colors.append((tweet_df.loc[tweet_df['in_reply_to_user_id'] == node]['marker_color']).values[0])
        else:
            blank_nodes.append(node)
    
def prune_network(network, blank_nodes):
    ''' Eliminate nodes with incomplete data'''
    for i in range(len(blank_nodes)):
        network.remove_node(blank_nodes[i])
        
def summarize_networks(network, subnetwork, filename):
    ''' Generate summary of network as txt file'''
        # Calculate degrees of each node
    degrees = [deg for (node, deg) in network.degree()]
    sub_degrees = [deg for (node, deg) in subnetwork.degree()]
    #subnet_degrees = dict(subnetwork.degree)
    
    with open(filename, 'w') as file_out:
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
    

    
    
def main():
	# Load pkl file
    tweet_df = pd.read_pickle('usa_sentiments_df.pkl')
    print('Loaded data.')
    
    # Sentiment Analysis
    #tweet_df['preprocessed'] = tweet_df.apply(
    #    lambda row: preprocess_tweet(row['tweet_text']), axis=1)
    #tweet_df['sentiment_score'] = tweet_df.apply(
    #    lambda row: sentiment_analysis(row['preprocessed']), axis=1)
    #tweet_df['interpretation'] = tweet_df.apply(
    #                        lambda row: evaluate(row['sentiment_score']), axis=1)
    tweet_df['marker_color'] = tweet_df.apply(
                            lambda row: mkr(row['interpretation']), axis=1)
    
    # Save pkl file
    tweet_df.to_pickle('usa_sentiments_df.pkl')
    
    # Build Network Graph
    network = nx.Graph()
    colors = []
    subnet_colors = []
    blank_nodes = []
    subnet_blank_nodes = []
    tweet_df['marker_color'] = tweet_df['marker_color'].astype('str')
    
    # Primary Network
    build_network(network, tweet_df)
    colorize_network(network, tweet_df, colors, blank_nodes)
    prune_network(network, blank_nodes)
            
    # Largest Subnetwork   
    subnetwork = network.subgraph(max(nx.connected_components(network), key=len))
    colorize_network(subnetwork, tweet_df, subnet_colors, subnet_blank_nodes)
    prune_network(subnetwork, subnet_blank_nodes)    
    

    
    # Generate summary of network
    summarize_networks(network, subnetwork, 'network_analysis-expanded-update-noRTorUM.txt')
            
    
    #plt.figure(figsize=(50,50))
    #pos = nx.spectral_layout(network)
    #nx.draw(network, node_color=colors)
    #plt.savefig('network-usa-update-spectral.jpg')
    
    plt.figure(figsize=(50,50))
    pos2 = nx.spring_layout(subnetwork)
    nx.draw(subnetwork, pos=pos2, node_color=subnet_colors)
            #node_size=[v * 1000 for v in subnet_degrees.values()])
    plt.savefig('test.jpg') #'subnet_spring_um_replies.jpg')

if __name__ == "__main__":
    main()
           