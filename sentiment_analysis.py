# General Imports
import errno
import gzip
import json
from datetime import datetime
import sys
import logging
import os
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import numpy as np
# Import Google Client Library
from google.cloud import language
# Import COVID-19 Data API
import COVID19Py

# Pandas Settings
pd.set_option('max_colwidth', 280)  # Capture full tweet
pd.set_option("display.max_rows", None, "display.max_columns", None)
# Handle date time conversions between pandas and matplotlib
register_matplotlib_converters()

# Access the Google NLP API
CLIENT = language.LanguageServiceClient()
# Access the COVID19Py API
COVID = COVID19Py.COVID19(
    url='https://covid19-api.kamaropoulos.com')   # Mirror


def make_datetime_dir(analysis_dir):
    '''Create a subdirectory in analysis_dir using date-time naming convention'''
    save_dir = os.path.join(analysis_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    try:
        os.makedirs(save_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Creation of the directory %s failed" % save_dir)
    return save_dir


def preprocess_tweet(status):
    ''' Return full text of tweet '''
    if hasattr(status, 'retweeted_status'):   # Check if retweet
        try:
            status = status.retweeted_status.text
        except AttributeError:
            status = status.retweeted_status.full_text
    else:
        try:
            status = status.extended_tweet.full_text
        except AttributeError:
            status = status.full_text

    # Lowercase
    status.lower()

    #

    return status


def sentiment_analysis(tweet):
    ''' Sentiment analysis on input '''
    document = language.types.Document(
        content=tweet,
        type='PLAIN_TEXT')

    response = CLIENT.analyze_sentiment(
        document=document,
        encoding_type='UTF32',
    )

    sentiment = response.document_sentiment

    return sentiment


def evaluate(score):
    ''' Sentiment analysis interpretation '''
    if score > 0.2:
        return '+'
    if -0.2 <= score <= 0.2:
        return ' '
    return 'v'


def mkr(interp):
    ''' Assign marker based on interpretation '''
    if interp == '+':
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
    plt.savefig('tweet_data.png')


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


def select_fn(acct):
    ''' Administrivia for acct '''
    print(acct.get())


def main():
    ''' COVID-19 Tweet Analysis '''
    
    # Constants
    DATE = '2020-01'
    
    # Define directories
    root_dir = '/projectnb/caad/meganmp/data/usa-tweets'
    analysis_dir = '/projectnb/caad/meganmp/analysis/results/sentiment_analysis/'
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
                                tweet = json.loads(line)
                                
                                tweet = preprocess_tweet(tweet)
                                #if any(keyword in tweet for keyword in (
                                        #'COVID', 'covid', 'China virus', 'coronavirus')):
                        
                                # Sentiment analysis
                                sentiment = sentiment_analysis(tweet)
                    
                                # Date Time format
                                date_time_str = str(status.created_at)
                                date_time = datetime.datetime.strptime(
                                    date_time_str, '%Y-%m-%d %H:%M:%S')
                    
                                # Store values
                                pd_df = pd.DataFrame({'Date': [date_time],
                                                      'ID': handle,
                                                      'Tweet': tweet,
                                                      'Sentiment_Score': [sentiment.score],
                                                      'Sentiment_Mag': [sentiment.magnitude]})
                                tweet_data = tweet_data.append(pd_df, ignore_index=True)
                    
                        tweet_data['Date'] = pd.to_datetime(
                            tweet_data['Date'], format='%Y-%m-%d %H:%M:%S')
                        tweet_data['Interpretation'] = tweet_data.apply(lambda row: evaluate(
                            row['Sentiment_Score']), axis=1)
                        tweet_data['Marker Color'] = tweet_data.apply(
                            lambda row: mkr(row['Interpretation']), axis=1)
                            
                                                   
    logging.info('[Twitter Data] Processing Complete')                          
    loop_end = datetime.now()
    loop_time = loop_end - loop_start
    logging.info('Loop Completion Time = %s', loop_time)
    
    visualize(tweet_data, covid_data)


if __name__ == "__main__":
    main()
