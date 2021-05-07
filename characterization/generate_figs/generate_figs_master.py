# -*- coding: utf-8 -*-
"""
COVID-19 Final Dataset: Figure Generation
Megan M. Parsons | meganmp@bu.edu
"""

# Imports
import csv
import emoji
from fuzzywuzzy import fuzz
import gzip
import json
import logging
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import unidecode
from collections import OrderedDict

# Define directories
root_dir = '/projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/'
save_dir = '/projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/' 

def open_json(file):
    with open(os.path.join(root_dir, file), 'r') as f:
        data = json.load(f)
    
    return data


def main():
    
    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'characterization_locations_usa.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Figure Generation Log of Final Dataset')
    
    # Set Seaborn theme
    sns.set_style('white')
    sns.set_context('paper')
    
    # Load data
    logging.info('Loading data')
    tweet_totals = open_json('monthly_totals-usa.json')
    locations = open_json('location_totals-usa.json')
    
    with open(os.path.join(root_dir, 'top100locations-usa.csv'), 'r') as f:
        data = csv.reader(f, delimiter=',')
        for row in data:
            print(row)
    top100locs = pd.read_csv(os.path.join(root_dir, 'top100locations-usa.csv'))
    
    # Format data
    logging.info('Formatting Tweet Totals')
    tweet_totals = pd.DataFrame(list(tweet_totals.items()),columns = ['Month','Total Tweets'])
    tweet_totals.set_index('Month')    
    
    ################# PLOTS ##################################################
    # Plot of tweet totals per month
    barplot = sns.barplot(x='Month',
                          y='Total Tweets',
                          data = tweet_totals)
    barplot.set(title = 'COVID-19 Tweets from Jan-Jun 2020',
                                                   xlabel='Month',
                                                   ylabel='Total Tweets (Thousands)')
    
    plt.ticklabel_format(style='plain', axis='y')
    yticks = barplot.get_yticks()/1000
    yticks = [int(x) for x in yticks]
    barplot.set_yticklabels(yticks)
    plt.show()
    
    # Plot top 100 locations on map
    print(top100locs)
    
    ###########################################################################
    # Can we associate similar locations based on Levenshtein distance?
    str1 = 'usa'
    str2 = 'USA'
    token_sort_ratio = fuzz.token_sort_ratio(str1, str2)
    print(token_sort_ratio)
    
    
    
    print('done')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # Save top 100 locations in csv
    logging.info('Saving top 100 locations csv')
    with open(os.path.join(save_dir, 'top100locations-usa.csv'), 'w') as f3:
        write = csv.writer(f3)
        write.writerow(top100locs)

    # Save location totals dictionary
    logging.info('Saving location totals')
    with open(os.path.join(save_dir, 'location_totals-usa.json'), 'w') as f4:
        json.dump(location_totals, f4)
        
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()

