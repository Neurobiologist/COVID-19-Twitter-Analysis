#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import json
import carmen
import os
from datetime import datetime
import sys
import logging

def main():
    # Day Number as a two-digit string
    DN = int(os.environ["SGE_TASK_ID"])
    DN = "%02d" % DN

    # Define directories
    root_dir = '/projectnb/caad/meganmp/data/english-tweets'
    save_dir = '/projectnb/caad/meganmp/data/usa-tweets'

    # Create log
    logging.basicConfig(filename='data-feb.log', level=logging.DEBUG, format='%(levelname)s\t%(asctime)s\t%(message)s') # MODIFY

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
            if date_dir != '2020-02':  #MODIFY
                continue
            logging.info('Processing: %s', date_dir)
            tweets = []
            tweet_num = 0
            start_3 = datetime.now()
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    day_string = "coronavirus-tweet-id-2020-02-" + DN  #MODIFY
                    if day_string not in file:
                        continue
                    with gzip.open(os.path.join(save_dir, date_dir, file), 'w') as file_out:
                        with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                            start_4 = datetime.now()
                            for line in gzip_file:
                                line = line.rstrip()
                                if line:
                                    tweet = json.loads(line)
                                    resolver = carmen.get_resolver()
                                    resolver.load_locations()
                                    location = resolver.resolve_tweet(tweet)
                                    try:
                                        if location[1].country == 'United States':
                                            file_out.write(line + b'\n')
                                            tweet_num += 1
                                    except:
                                        continue
                            end_4 = datetime.now()
                            time_4 = end_4 - start_4
                            logging.info('Time4 = %s', time_4)
            monthly_totals[date_dir] = tweet_num
            end_3 = datetime.now()
            time_3 = end_3 - start_3
            logging.info('Time3 = %s', time_3)
        end_2 = datetime.now()
        time_2 = end_2 - start_2
        logging.info('Time2 = %s', time_2)
    end_1 = datetime.now()
    time_1 = end_1 - start_1
    logging.info('Time1 = %s', time_1)
                
    # Save monthly totals dictionary
    print('Saving monthly totals')
    with open('/projectnb/caad/meganmp/analysis/preprocessing/feb.json', 'w', encoding='utf-8') as f:
        json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
    
    logging.info('Preprocessing Complete')

if __name__ == '__main__':
    main()
