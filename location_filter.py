#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 12:56:49 2021

@author: meganmp
"""
print('Load imports')
import gzip
import json
import carmen

# Define directories
root_dir = '/projectnb/caad/meganmp/data/english-tweets'	 
save_dir = '/projectnb/caad/meganmp/data/usa-tweets' 

# Initialize variables
monthly_totals = dict()
count = 0

# Traverse the data
for sub_dir, dirs, files in os.walk(root_dir):
    dirs.sort()
    files.sort()
    for date_dir in sorted(dirs):
        print(date_dir)
        tweets = []
        tweet_num = 0
        for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
            file_extension = os.path.splitext(file)[1]
            if file_extension == '.gz':
                print(file)
                with gzip.open(os.path.join(save_dir, date_dir, file), 'w') as file_out:
                    with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                        for line in gzip_file:
                            line = line.rstrip()
                            if line:
                                tweet = json.loads(line)
                                resolver = carmen.get_resolver()
                                resolver.load_locations()
                                location = resolver.resolve_tweet(tweet)
                                if location[1].country == 'United States':
                                    file_out.write(line + b'\n')
                                    count += 1
                                    tweet_num += 1
        monthly_totals[date_dir] = tweet_num
        print(monthly_totals)
                
# Save monthly totals dictionary
print('Saving monthly totals')
with open('/projectnb/caad/meganmp/analysis/monthly_totals-usa.json', 'w', encoding='utf-8') as f:
    json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
    
print('Preprocessing Complete')