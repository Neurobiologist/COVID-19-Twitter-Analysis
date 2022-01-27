# -*- coding: utf-8 -*-
"""
COVID-19 Final Dataset Characterization
Megan M. Parsons | meganmp [at] bu [dot] edu
"""

# Imports
import gzip
import json
import logging
import os
from collections import OrderedDict

# Define directories
root_dir = '/data/usa-tweets/'
save_dir = '/analysis/results/characterization/usa-tweets/' 

def rank_locations(loc_dict):
    ''' Return top 100 locations from location dictionary'''
    loc_dict = OrderedDict(sorted(loc_dict.items(), key=lambda x: x[1], reverse=True))
    first_n_values = list(loc_dict.items())[:100]
    return first_n_values


def main():
    
    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'characterization_usa.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Characterization Log of Final Dataset')
    
    # Initialize variables
    logging.info('Initialize dictionaries')
    monthly_totals = dict()
    language_totals = dict()    
    
    # Traverse the data
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for date_dir in sorted(dirs):
            logging.info('Processing %s', date_dir)
            tweet_num = 0
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
                                    tweet_num += 1
            
                                    # Language Frequency
                                    if tweet_content['lang'] == None:
                                        tweet_content['lang'] = 'none'
                                    if tweet_content['lang'] in language_totals:
                                        language_totals[tweet_content['lang']] += 1
                                    else:
                                        language_totals[tweet_content['lang']] = 1
                        except:
                            continue

            monthly_totals[date_dir] = tweet_num
            logging.info('Monthly Total: %s\t%d', date_dir, tweet_num)
                
    logging.info('TRAVERSING DATA COMPLETE')
    
    # Save monthly totals dictionary
    logging.info('Saving monthly totals')
    with open(os.path.join(save_dir, 'monthly_totals-usa.json'), 'w', encoding='utf-8') as f:
        json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
        
    # Save language totals dictionary
    logging.info('Saving language totals')
    with open(os.path.join(save_dir, 'language_totals-usa.json'), 'w') as f2:
        json.dump(language_totals, f2)  
        
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
            
