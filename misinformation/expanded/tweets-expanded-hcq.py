'''
Isolate and Characterize Hydroxychloroquine Tweets (Modified for expanded dataset)
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
import unidecode
from collections import OrderedDict

# Define directories
root_dir = '/projectnb/caad/meganmp/data/usa-tweets/'
save_dir = '/projectnb/caad/meganmp/data/misinformation/expanded/' 

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
    logging.info('Start Misinformation Log of USA Dataset HCQ Tweets - Expanded')
    
    # Initialize variables
    logging.info('Initialize dictionary')
    location_totals = dict()  
    
    # Traverse the data
    with gzip.open(os.path.join(save_dir, 'hcq-expanded-tweets.jsonl.gz'), 'w') as file_out:
        for sub_dir, dirs, files in os.walk(root_dir):
            dirs.sort()
            files.sort()
            for date_dir in sorted(dirs):
                print(date_dir)
                if (date_dir == '2020-01') or (date_dir == '2020-02'):
                    continue
                logging.info('Processing %s', date_dir)
                for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                    file_extension = os.path.splitext(file)[1]
                    if file_extension == '.gz':
                        logging.info('Processing %s', file)
                        with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                            try:
                                for line in gzip_file:
                                    line = line.rstrip()
                                    if line:
                                        tweet_content = json.loads(line)
                                        
                                        # Identify Keywords
                                        try:
                                            if ('hydroxychloroquine' in tweet_content['entities']['hashtags'][0]['text']) or \
                                            ('chloroquine' in tweet_content['entities']['hashtags'][0]['text']) or \
                                            ('HCQ' in tweet_content['entities']['hashtags'][0]['text']):
                                                file_out.write(line + b'\n')
                                                
                                                # Process Location Data
                                                location = tweet_content['user']['location']
                                                location = preprocess_location(location)
                                                
                                                # Location Frequency
                                                if location == None or type(location) != str:
                                                    location = 'none'
                                                if location in location_totals:
                                                    location_totals[location] += 1
                                                else:
                                                    location_totals[location] = 1
                                                    
                                            elif ('hydroxychloroquine' in tweet_content['full_text']) or \
                                                ('chloroquine' in tweet_content['full_text']) or \
                                                ('HCQ' in tweet_content['full_text']):
                                                    file_out.write(line + b'\n')
                                                
                                                    # Process Location Data
                                                    location = tweet_content['user']['location']
                                                    location = preprocess_location(location)
                                                    
                                                    # Location Frequency
                                                    if location == None or type(location) != str:
                                                        location = 'none'
                                                    if location in location_totals:
                                                        location_totals[location] += 1
                                                    else:
                                                        location_totals[location] = 1
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
    with open(os.path.join(save_dir, 'top100locations-hcq-expanded.csv'), 'w') as f3:
        write = csv.writer(f3)
        write.writerow(top100locs)

    # Save location totals dictionary
    logging.info('Saving location totals')
    with open(os.path.join(save_dir, 'location_totals-hcq-expanded.json'), 'w') as f4:
        json.dump(location_totals, f4)
        
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
            
        
        

      




