# General Imports
import emoji
import errno
import gzip
import json
import logging
import matplotlib.pyplot as plt
import nltk
import numpy as np
import os
import pandas as pd
import re
import sys
from datetime import datetime
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pandas.plotting import register_matplotlib_converters

# Import Google Client Library
from google.cloud import language
# Import COVID-19 Data API
import COVID19Py

# Pandas Settings
pd.set_option('max_colwidth', 280)  # Capture full tweet
pd.set_option("display.max_rows", None, "display.max_columns", None)
# Handle date time conversions between pandas and matplotlib
register_matplotlib_converters()

# NLTK Setup
nltk.download('all')

# Access the Google NLP API
CLIENT = language.LanguageServiceClient()
# Access the COVID19Py API
COVID = COVID19Py.COVID19(
    url='https://covid19-api.kamaropoulos.com')   # Mirror


def make_datetime_dir(analysis_dir):
    '''Create a subdirectory in analysis_dir using date-time naming convention'''
    save_dir = os.path.join(
        analysis_dir,
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    try:
        os.makedirs(save_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Creation of the directory %s failed" % save_dir)
    return save_dir


def serialize(line):
    ''' Load, serialize, and preprocess Tweet'''
    # Decode Binary and Load into Python Dictionary
    tweet_dict = json.loads(line)

    return tweet_dict


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


def mkr(interp):
    ''' Assign marker based on interpretation '''
    if interp == '+' or interp == '++':
        return 'b'
    if interp == ' ':
        return 'k'
    return 'r'


def tweet_polarity(tweet_data):
    ''' Plot histogram of tweet data '''
    plt.hist(tweet_data['Sentiment_Score'], bins='auto')
    plt.title(
        'COVID-19 Sentiment Distribution for @{}'.format(tweet_data['ID'][0]))
    plt.xlabel('Sentiment Score')
    plt.xlim(-1, 1)
    plt.show()
    # plt.savefig('tweet_data.png')


def covid_plot(tweet_data, covid_data):
    ''' Create plot of COVID-19 data '''
    _, ax_plot = plt.subplots(2, 1, sharex=True, figsize=(20, 10))
    ax_plot[0].plot(covid_data['Date'], covid_data['Confirmed Cases'])
    ax_plot[0].set_title('Cases of COVID-19 in the United States')
    ax_plot[0].set_ylabel('Confirmed Cases of COVID-19')

    # Create plot of Twitter Sentiment and Magnitude Data
    for x_idx, y_idx, sent_idx, color_idx, marker_idx in zip(
            tweet_data['Date'].to_list(),
            tweet_data['Sentiment_Mag'].to_list(),
            100 * np.ones(len(
                tweet_data['Marker Color'].to_list())),
            tweet_data['Marker Color'].to_list(),
            tweet_data['Interpretation'].to_list()):
        ax_plot[1].scatter(
            x_idx,
            y_idx,
            s=sent_idx,
            c=color_idx,
            marker=marker_idx)
    ax_plot[1].set_title('COVID-19 Tweet Sentiment')
    ax_plot[1].set_ylabel('Sentiment Magnitude')
    ax_plot[1].tick_params(axis='x', rotation=45)

    # Format plots
    plt.tight_layout()
    plt.xlabel('Date')
    plt.show()
    plt.savefig('covid_plot.png')


def visualize(tweet_data, covid_data):
    ''' Create visualizations of data '''
    tweet_polarity(tweet_data)    # Overview of Tweet Data
    covid_plot(tweet_data, covid_data)


def main():
    ''' COVID-19 Tweet Analysis '''

    # Constants
    DATE = '2020-01'

    # Define directories
    root_dir = '/data/usa-tweets'
    analysis_dir = '/analysis/results/sentiment_analysis/'
    save_dir = make_datetime_dir(analysis_dir)

    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'sentiment_analysis.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Sentiment Analysis Log')

    # Process Ground Truth COVID-19 Data
    logging.info('[Ground Truth COVID-19 Data] Processing')
    location = COVID.getLocationByCountryCode("US", timelines=True)
    raw_data = location[0]['timelines']['confirmed']['timeline']
    covid_data = pd.DataFrame.from_dict(raw_data, orient='index')
    covid_data = covid_data.reset_index()
    covid_data.columns = ['Date', 'Confirmed Cases']
    covid_data['Date'] = pd.to_datetime(
        covid_data.Date, format='%Y-%m-%dT%H:%M:%SZ')
    logging.info('[Ground Truth COVID-19 Data] Processing Complete')

    # Process Twitter Data
    logging.info('[Twitter Data] Processing')
    # Create Twitter Dataframe
    tweet_data = pd.DataFrame()

    # Initialize variables
    monthly_totals = dict()

    # Day Number as a two-digit string
    #day_numbers = int(os.environ["SGE_TASK_ID"])
    #DN = "%02d" % DN
    DN = 25

    loop_start = datetime.now()
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for date_dir in sorted(dirs):
            if date_dir != DATE:
                continue
            logging.info('Processing: %s', date_dir)
            tweets = []
            tweet_num = 0
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    day_string = "coronavirus-tweet-id-" + DATE + "-" + str(DN)
                    if day_string not in file:
                        continue
                    with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                        for line in gzip_file:
                            line = line.rstrip()
                            if line:
                                # Load, serialize, and preprocess line
                                tweet_obj = serialize(line)

                                # Preprocess json_obj
                                tweet = preprocess_tweet(tweet_obj)
                                # if any(keyword in tweet for keyword in (
                                # 'COVID', 'covid', 'China virus', 'coronavirus')):

                                # To obtain hashtag list:
                                # hashtags =  tweet_obj['entities']['hashtags'][0]['text']

                                # Sentiment analysis
                                sentiment = sentiment_analysis(tweet)

                                # Date Time format
                                date_time_str = str(tweet_obj['created_at'])
                                date_time = datetime.strftime(
                                    datetime.strptime(
                                        date_time_str,
                                        '%a %b %d %H:%M:%S +0000 %Y'),
                                    '%Y-%m-%d %H:%M:%S')

                                # Store values
                                pd_df = pd.DataFrame({'Date': [date_time],
                                                      'ID': handle,
                                                      'Tweet': tweet,
                                                      'Sentiment_Score': [sentiment.score],
                                                      'Sentiment_Mag': [sentiment.magnitude]})
                                tweet_data = tweet_data.append(
                                    pd_df, ignore_index=True)

                        tweet_data['Date'] = pd.to_datetime(
                            tweet_data['Date'], format='%Y-%m-%d %H:%M:%S')
                        tweet_data['Interpretation'] = tweet_data.apply(
                            lambda row: evaluate(row['Sentiment_Score']), axis=1)
                        tweet_data['Marker Color'] = tweet_data.apply(
                            lambda row: mkr(row['Interpretation']), axis=1)

    loop_end = datetime.now()
    loop_time = loop_end - loop_start
    logging.info('Loop Completion Time = %s', loop_time)
    logging.info('[Twitter Data] Processing Complete')

    visualize(tweet_data, covid_data)


if __name__ == "__main__":
    main()
