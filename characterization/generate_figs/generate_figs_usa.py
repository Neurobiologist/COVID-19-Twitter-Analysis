# -*- coding: utf-8 -*-
"""
COVID-19 Final Dataset: Figure Generation
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
root_dir = '/projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/'
save_dir = '/projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/' 

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
        filename=os.path.join(save_dir, 'characterization_locations_usa.log'),
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
    tweet_totals = open_json('monthly_totals-usa.json')
    locations = open_json('location_totals-usa.json')
    top100locations = open_locs_csv('top100locations-usa.csv')
    map_dict = json.load( open( "location_map_dict.json" ) ) # Equivalent to location_map_dict below
    
    # Format data
    logging.info('Formatting Tweet Totals')
    tweet_totals = pd.DataFrame(list(tweet_totals.items()),columns = ['Month','Total Tweets'])
    tweet_totals.set_index('Month')    
    
    ################# PLOTS ##################################################
    # Plot of tweet totals per month
    # barplot = sns.barplot(x='Month',
    #                       y='Total Tweets',
    #                       data = tweet_totals)
    # barplot.set(title = 'COVID-19 Tweets from Jan-Jun 2020',
    #                                                xlabel='Month',
    #                                                ylabel='Total Tweets (Thousands)')
    
    # plt.ticklabel_format(style='plain', axis='y')
    # yticks = barplot.get_yticks()/1000
    # yticks = [int(x) for x in yticks]
    # barplot.set_yticklabels(yticks)
    # barplot.figure.savefig('usa_tweet_volume.jpg')
    # barplot.figure.savefig('usa_tweet_volume.png')
    
    # Plot top 100 locations on map
    # Generate Map
    # usa_tweets_map = folium.Map(location=[39, -100], zoom_start=4)
    # labeled_map = folium.Map(location=[39, -100], zoom_start=4)
    
    # Plot location markers on map
    # geolocator = Nominatim(user_agent='Class_Project')
    # for key in top100locations.keys():
    #     try:
    #         user_location = geolocator.geocode(key, country_codes='us')
    #     except:
    #         continue
    #     if user_location:
    #         folium.Marker([user_location.latitude, user_location.longitude], popup=user_location.address).add_to(usa_tweets_map)
    #         folium.Marker([user_location.latitude, user_location.longitude], popup=key).add_to(labeled_map)
    #         location_map_dict[key] = [[user_location.latitude, user_location.longitude], user_location.address]
            
            
    # usa_tweets_map.save('usa_tweets_map.html')
    # labeled_map.save('labeled_map.html')
    # json.dump(location_map_dict, open( "location_map_dict.json", 'w' ) )
                
        
        
        
    
    ###########################################################################
    # Can we associate similar locations based on Levenshtein distance?
    str1 = 'usa'
    str2 = 'USA'
    token_sort_ratio = fuzz.token_sort_ratio(str1, str2)
    print(token_sort_ratio)
    
    for key, value in map_dict.items():
        for key2, value2 in map_dict.items():
            print('{}, {}: {}'.format(key, key2, fuzz.token_sort_ratio(key, key2)))
    
    
    # What if we associate the same identified locations in the top 100 locations
    # in the USA with the keys; does this mean that those keys in the flipped
    # dictionary are equivalent?
    consolidated_locs = dict()
    
    for key, value in map_dict.items():
        if value[1] not in consolidated_locs:
            consolidated_locs[value[1]] = [key]
        else:
            consolidated_locs[value[1]].append(key)
    
    print(consolidated_locs)
    consolidated_locs_length = len(consolidated_locs)
    # CONCLUSION: Our top 100 list is actually a top 72 list.
    
    
    
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

