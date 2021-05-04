# -*- coding: utf-8 -*-
"""
COVID-19 Twitter Analysis: Preprocessing Pipeline
Megan M. Parsons | meganmp@bu.edu
INSTRUCTIONS: To run, type into terminal: ./preprocessing.py >> out.txt 
"""

# Imports
import gzip
import json
import logging
import os
from collections import Counter
from pprint import pprint as pp

# Define directories
root_dir = '/projectnb/caad/meganmp/data/COVID-19-TweetIDs-master'
save_dir = '/projectnb/caad/meganmp/data/english-tweets'

def main():
    ''' Preprocess COVID-19 Twitter Data'''
    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'characterization_locations_original.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Characterization Log of Original Dataset Locations')
    
    # Initialize variables
    logging.info('Preprocessing Pipeline Started')
    logging.info('Initializing variables')
    monthly_totals = dict()
    
    # Traverse the data
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for date_dir in sorted(dirs):
            logging.info('Processing %s', date_dir)
            tweets = []
            tweet_num = 0
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    logging.info(file)
                    with gzip.open(os.path.join(save_dir, date_dir, file), 'w') as file_out:
                        with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                            for line in gzip_file:
                                line = line.rstrip()
                                if line:
                                    tweet_content = json.loads(line)
                                    if tweet_content['lang'] == 'en':	# Filter out non-English Tweets
                                        file_out.write(line + b'\n')
                                        tweet_num += 1
                    
            monthly_totals[date_dir] = tweet_num
            logging.info('Monthly Total: %d', tweet_num)             

    logging.info('TRAVERSING DATA COMPLETE')
    
    # Save monthly totals dictionary
    logging.info('Saving monthly totals')
    with open('/projectnb/caad/meganmp/analysis/monthly_totals-english.json', 'w', encoding='utf-8') as f:
        json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
    
    logging.info('Initializing Counter')
    c = Counter(x['user']['location'] for x in tweets)
    logging.info('Counter Complete')
    location_totals = dict(c)
    logging.info('Counter converted to dictionary')
    pp(location_totals)
    
    # Save location totals dictionary
    logging.info('Saving location totals')
    with open('/projectnb/caad/meganmp/analysis/location_totals-english.json', 'w') as f2:
        json.dump(location_totals, f2)
    
    logging.info('Preprocessing Complete')
    
    
if __name__ == "__main__":
    main()
           
            
        
        

      




