#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import json
import carmen
import os
from datetime import datetime
import sys
import logging
 
#class Logger:
 
    #def __init__(self, filename):
        #self.console = sys.stdout
        #self.file = open(filename, 'w')
 
    #def write(self, message):
        #self.console.write(message)
        #self.file.write(message)
 
    #def flush(self):
        #self.console.flush()
        #self.file.flush()

def main():
    # Define directories
    root_dir = '/projectnb/caad/meganmp/data/english-tweets'
    save_dir = '/projectnb/caad/meganmp/data/us-tweets'

    # Create log
    #path = '/projectnb/caad/meganmp/analysis/us-tweets-log.txt'
    #sys.stdout = Logger(path)
    logging.basicConfig(filename='location-us.log', level=logging.INFO, format='%(levelname)s\t%(message)s')

    # Initialize variables
    monthly_totals = dict()

    # Traverse the data
    logging.info('Started')
    start_1 = datetime.now()
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        start_2 = datetime.now()
        for date_dir in sorted(dirs):
            logging.info('Processing: %s', date_dir)
            tweets = []
            tweet_num = 0
            start_3 = datetime.now()
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    with gzip.open(os.path.join(save_dir, date_dir, file), 'w') as file_out:
                        with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                            start_4 = datetime.now()
                            for line in gzip_file:
                                line = line.rstrip()
                                if line:
                                    tweet = json.loads(line)
                                    #resolver = carmen.get_resolver()
                                    #resolver.load_locations()
                                    #location = resolver.resolve_tweet(tweet)
                                    try:
                                        #if location[1].country == 'United States':
                                         if tweet['place']['country_code'] == 'US':
                                            file_out.write(line + b'\n')
                                            tweet_num += 1
                                    except:
                                        continue
                            end_4 = datetime.now()
                            time_4 = end_4 - start_4
                            logging.debug('Time4 = %s', time_4)
            monthly_totals[date_dir] = tweet_num
            end_3 = datetime.now()
            time_3 = end_3 - start_3
            logging.debug('Time3 = %s', time_3)
        end_2 = datetime.now()
        time_2 = end_2 - start_2
        logging.debug('Time2 = %s', time_2)
    end_1 = datetime.now()
    time_1 = end_1 - start_1
    logging.debug('Time1 = %s', time_1)
                
    # Save monthly totals dictionary
    print('Saving monthly totals')
    with open('/projectnb/caad/meganmp/analysis/monthly_totals-us-tweets.json', 'w', encoding='utf-8') as f:
        json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
    
    logging.info('Preprocessing Complete')

if __name__ == '__main__':
    main()
