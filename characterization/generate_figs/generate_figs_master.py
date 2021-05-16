# -*- coding: utf-8 -*-
"""
COVID-19 Original Dataset: Figure Generation
Megan M. Parsons | meganmp@bu.edu
"""

# Imports
import csv
import emoji
import folium
from geopy.geocoders import Nominatim
import gzip
import json
import logging
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import unidecode
from fuzzywuzzy import fuzz
from collections import OrderedDict

# Define directories
root_dir = '/projectnb/caad/meganmp/analysis/results/characterization/master/'
save_dir = '/projectnb/caad/meganmp/analysis/results/characterization/master/'


def open_json(file):
    with open(os.path.join(root_dir, file), 'r') as f:
        data = json.load(f)
    return data


def open_locs_csv(file):
    ''' Convert top 100 locations csv to Python dictionary'''
    # Intialize Variables
    loc_dict = dict()
    # Conversion from csv to dict
    with open(os.path.join(root_dir, file), 'r') as f:
        data = csv.reader(f, delimiter=',')
        for row in data:
            for i in range(len(row)):
                tup = eval(row[i])
                loc_dict.setdefault(tup[0], []).append(tup[1])
    return loc_dict


def main():

    # Create log
    logging.basicConfig(
        filename=os.path.join(
            save_dir, 'characterization_locations_master.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Figure Generation Log of Final Dataset')

    # Set Seaborn theme
    sns.set_style('white')
    sns.set_context('paper')

    # Initialize variables
    location_map_dict = dict()

    # Load data
    logging.info('Loading data')
    tweet_totals = open_json('monthly_totals-master.json')
    locations = open_json('location_totals-master.json')
    top100locations = open_locs_csv('top100locations-master.csv')

    # Format data
    logging.info('Formatting Tweet Totals')
    tweet_totals = pd.DataFrame(list(tweet_totals.items()), columns=[
                                'Month', 'Total Tweets'])
    tweet_totals.set_index('Month')

    ################# PLOTS ##################################################
    # Plot of tweet totals per month
    # Plot of tweet totals per month
    barplot = sns.barplot(x='Month',
                          y='Total Tweets',
                          data=tweet_totals)
    barplot.set(title='COVID-19 Tweets from Jan-Jun 2020',
                xlabel='Month',
                ylabel='Total Tweets (Millions)')

    plt.ticklabel_format(style='plain', axis='y')
    plt.yticks(barplot.get_yticks(), barplot.get_yticks() /1000000)
    #yticks = barplot.get_yticks()/1000
    #yticks = [int(x) for x in yticks]
    #barplot.set_yticklabels(yticks)
    plt.setp(barplot.get_xticklabels(), rotation=45)
    plt.figure(figsize=(32, 24))
    sns.set(font_scale=1)
    barplot.figure.savefig('/projectnb/caad/meganmp/analysis/results/characterization/master/master_tweet_volume.jpg', bbox_inches = "tight")

    # Plot top 100 locations on map
    master_tweets_map = folium.Map()

    # Plot location markers on map
    geolocator = Nominatim(user_agent='Class_Project')
    for key in top100locations.keys():
        try:
            user_location = geolocator.geocode(key)
        except:
            continue
        if user_location:
            folium.Marker([user_location.latitude, user_location.longitude],
                          popup=user_location.address).add_to(master_tweets_map)
            location_map_dict[key] = [[user_location.latitude,
                                       user_location.longitude], user_location.address]

    master_tweets_map.save('master_tweets_map.html')
    json.dump(location_map_dict, open("master_location_map_dict.json", 'w'))

    ###########################################################################
    # # Can we associate similar locations based on Levenshtein distance?
    # str1 = 'usa'
    # str2 = 'USA'
    # token_sort_ratio = fuzz.token_sort_ratio(str1, str2)
    # print(token_sort_ratio)

    # What if we associate the same identified locations in the top 100 locations
    # in the USA with the keys; does this mean that those keys in the flipped
    # dictionary are equivalent?
    consolidated_locs = dict()

    for key, value in location_map_dict.items():
        if value[1] not in consolidated_locs:
            consolidated_locs[value[1]] = [key]
        else:
            consolidated_locs[value[1]].append(key)

    print(consolidated_locs)
    consolidated_locs_length = len(consolidated_locs)
    # CONCLUSION: Top 100 locaitons is actually representative of 82 locations.
    # 

    print('done')
    
    


if __name__ == "__main__":
    main()
