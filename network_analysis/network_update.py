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
    #interactions.add((str(row["retweeted_id"]), str(row["retweeted_screen_name"])))
    # User Mentions
    #interactions.add((str(row["user_mention_id"]), str(row["user_mention_screen_name"])))
    
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
        return 'teal'
    if interp == '+':
        return 'lightblue'
    if interp == ' ':
        return 'moccasin'
    if interp == '-':
        return 'mistyrose'
    return 'maroon'


def tweet_polarity(tweet_data):
    ''' Plot histogram of tweet data '''
    plt.hist(tweet_data['Sentiment_Score'], bins='auto')
    plt.title(
        'COVID-19 Sentiment Distribution for @{}'.format(tweet_data['ID'][0]))
    plt.xlabel('Sentiment Score')
    plt.xlim(-1, 1)
    plt.show()
    # plt.savefig('tweet_data.png')

def main():
	# Load pkl file
    tweet_df = pd.read_pickle('usa_sentiments_df.pkl')
    print('Loaded data.')
    
    """
    # Sentiment Analysis
    tweet_df['preprocessed'] = tweet_df.apply(
        lambda row: preprocess_tweet(row['tweet_text']), axis=1)
    tweet_df['sentiment_score'] = tweet_df.apply(
        lambda row: sentiment_analysis(row['preprocessed']), axis=1)
    tweet_df['interpretation'] = tweet_df.apply(
                            lambda row: evaluate(row['sentiment_score']), axis=1)
    tweet_df['marker_color'] = tweet_df.apply(
                            lambda row: mkr(row['interpretation']), axis=1)
    
    # Save pkl file
    tweet_df.to_pickle('usa_sentiments_df.pkl')
    """
    
    # Build Network Graph
    network = nx.Graph()
    colors = []
    
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
               
    for node in network:
        if node in tweet_df['user_id'].values:
            colors = colors.append(tweet_df.loc[tweet_df['user_id'] == node]['marker_color'])
        else: colors = colors.append("moccasin")
    
    # Identify largest subnetwork
    subnetwork = network.subgraph(max(nx.connected_components(network), key=len))
    
    # Calculate degrees of each node
    degrees = [deg for (node, deg) in network.degree()]
    sub_degrees = [deg for (node, deg) in subnetwork.degree()]
            
    with open('network_analysis-expanded-update-noRTorUM.txt', 'w') as file_out:
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
    

    plt.figure(figsize=(50,50))
    nx.draw(network)
    plt.savefig('network-usa-update-noRToruM-color.jpg')
    
    plt.figure(figsize=(50,50))
    nx.draw(subnetwork)
    plt.savefig('subnetwork-usa-update-noRToruM-color.jpg')

if __name__ == "__main__":
    main()
           