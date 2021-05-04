# -*- coding: utf-8 -*-
"""
COVID-19 Original Dataset Characterization
Megan M. Parsons | meganmp@bu.edu
"""

# Imports
import csv
import gzip
import json
import logging
import os
from collections import OrderedDict

# Define directories
root_dir = '/projectnb/caad/meganmp/data/COVID-19-TweetIDs-master'
save_dir = '/projectnb/caad/meganmp/analysis/results/characterization' 

def rank_locations(loc_dict):
    ''' Return top 100 locations from location dictionary'''
    loc_dict = OrderedDict(sorted(loc_dict.items(), key=lambda x: x[1], reverse=True))
    first_n_values = list(loc_dict.items())[:100]
    return first_n_values


def main():
    
    # Create log
    logging.basicConfig(
        filename=os.path.join(save_dir, 'characterization_original.log'),
        level=logging.DEBUG,
        format='%(levelname)s\t%(asctime)s\t%(message)s')
    logging.info('Start Characterization Log of Original Dataset')
    
    # Initialize variables
    monthly_totals = dict()
    location_totals = dict()
    language_totals = dict()    
    
    # Traverse the data
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for date_dir in sorted(dirs):
            tweet_num = 0
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                        for line in gzip_file:
                            line = line.rstrip()
                            if line:
                                tweet_content = json.loads(line)
                                
                                # Location Frequency
                                if tweet_content['geo'] in location_totals:
                                    location_totals[tweet_content['geo']] += 1
                                else:
                                    location_totals[tweet_content['geo']] = 1
        
                                # Language Frequency
                                if tweet_content['lang'] in language_totals:
                                    language_totals[tweet_content['lang']] += 1
                                else:
                                    language_totals[tweet_content['lang']] = 1

            monthly_totals[date_dir] = tweet_num           
                
    logging.info('TRAVERSING DATA COMPLETE')
    
    # Rank top 100 locations
    logging.info('Ranking top 100 locations')
    top100locs = rank_locations(location_totals)
    
    # Save monthly totals dictionary
    logging.info('Saving monthly totals')
    with open(os.path.join(save_dir, 'monthly_totals-master.json'), 'w', encoding='utf-8') as f:
        json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
        
    # Save language totals dictionary
    logging.info('Saving language totals')
    with open(os.path.join(save_dir, 'language_totals-master.json'), 'w') as f2:
        json.dump(language_totals, f2)  
        
    # Save top 100 locations in csv
    logging.info('Saving top 100 locations csv')
    with open(os.path.join(save_dir, 'top100locations-master.csv'), 'w') as f3:
        write = csv.writer(f3)
        write.writerow(top100locs)

    # Save location totals dictionary
    logging.info('Saving location totals')
    with open(os.path.join(save_dir, 'location_totals-master.json'), 'w') as f4:
        json.dump(location_totals, f4)
        
    logging.info('Preprocessing Complete')


if __name__ == "__main__":
    main()
            
        
        

      




