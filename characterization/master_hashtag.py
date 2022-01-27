# -*- coding: utf-8 -*-
"""
COVID-19 Original Dataset Characterization of Self-Reported Locations
Megan M. Parsons | meganmp [at] bu [dot] edu
"""

# Imports
import csv
import emoji
import gzip
import json
import logging
import os
import unidecode
from collections import OrderedDict

# Define directories
root_dir = '/data/COVID-19-TweetIDs-master'
save_dir = '/analysis/results/master_hashtags' 

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
        filename=os.path.join(save_dir, 'characterization_locations_original.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Characterization Log of Original Dataset Locations')
    
    # Initialize variables
    logging.info('Initialize dictionary')
    hashtag_totals = dict()  
    is_geotagged = 0
    
    # Traverse the data
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for date_dir in sorted(dirs):
            logging.info('Processing %s', date_dir)
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    logging.info('Processing %s', file)
                    with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                        for line in gzip_file:
                            line = line.rstrip()
                            if line:
                                tweet_content = json.loads(line)
                                
                                try:
                                        
                                    hashtags = tweet_content['entities']['hashtags'][0]['text']
                                    # Location Frequency

                                    if hashtags in hashtag_totals:
                                        hashtag_totals[hashtags] += 1
                                    else:
                                        hashtag_totals[hashtags] = 1
                                except:
                                    continue
                                    
                                if tweet_content['geo'] != None:
                                    is_geotagged += 1
                
    logging.info('TRAVERSING DATA COMPLETE')
    # Save location totals dictionary
    logging.info('Saving geotag totals')

    # Save location totals dictionary
    logging.info('Saving hashtag totals')
    with open(os.path.join(save_dir, 'hashtag_totals-master.json'), 'w') as f4:
        json.dump(hashtag_totals, f4)
        
    with open(os.path.join(save_dir, 'geotagged_master.txt'), 'w') as f:
        f.write('%d' % is_geotagged)

    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
            
