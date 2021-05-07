'''
Hydroxychloroquine Tweets: Analyze Keywords and Timeline
COVID-19 Analysis | meganmp@bu.edu
'''

# -*- coding: utf-8 -*-
"""
COVID-19 Original Dataset Characterization of Self-Reported Locations
Megan M. Parsons | meganmp@bu.edu
"""

# Imports
import csv
import emoji
import gzip
import json
import logging
import os
import pandas as pd
import unidecode
from collections import OrderedDict

# Define directories
root_dir = '/projectnb/caad/meganmp/data/misinformation/' 
save_dir = '/projectnb/caad/meganmp/analysis/results/misinformation/keywords'

def rank_locations(loc_dict):
    ''' Return top 100 locations from location dictionary'''
    loc_dict = OrderedDict(sorted(loc_dict.items(), key=lambda x: x[1], reverse=True))
    first_n_values = list(loc_dict.items())[:100]
    return first_n_values


def remove_emoji(loc):
    return emoji.get_emoji_regexp().sub(r'', loc)

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
    
    # Traverse the data
    with gzip.open(os.path.join(root_dir, 'hcq-tweets.jsonl.gz'), 'r') as gzip_file:
        try:
            for line in gzip_file:
                line = line.rstrip()
                if line:
                    tweet_obj = json.loads(line)
                                        
                    # Format into Pandas dataframe
                    try:
                        if 'hydroxychloroquine' in tweet_obj['entities']['hashtags'][0]['text']:
                            
                            # Process Location Data
                            location = tweet_content['user']['location']
                            location = preprocess_location(location)
                            
                    except:
                        continue
        except:
            continue
                                    

                
    logging.info('TRAVERSING DATA COMPLETE')
    
    # Rank top 100 locations
    logging.info('Ranking top 100 locations')
    top100locs = rank_locations(location_totals)
        
    # Save top 100 locations in csv
    logging.info('Saving top 100 locations csv')
    with open(os.path.join(save_dir, 'top100locations-hcq.csv'), 'w') as f3:
        write = csv.writer(f3)
        write.writerow(top100locs)

    # Save location totals dictionary
    logging.info('Saving location totals')
    with open(os.path.join(save_dir, 'location_totals-hcq.json'), 'w') as f4:
        json.dump(location_totals, f4)
        
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
            
        
        

      




