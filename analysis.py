# -*- coding: utf-8 -*-
"""
COVID-19 Twitter Analysis
Megan M. Parsons | meganmp@bu.edu
"""

# Imports
from collections import Counter
import gzip
import json
import os
import pickle as pkl
from pprint import pprint as pp

# Define directories
root_dir = '/projectnb/caad/meganmp/COVID-19-TweetIDs-master/'

# Initialize variables
monthly_totals = dict()

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
                with gzip.open(os.path.join(sub_dir, date_dir, file), 'rb') as gzip_file:
                    for line in gzip_file:
                        line = line.rstrip()
                        if line:
                            tweet_content = json.loads(line)
                            if tweet_content['lang'] != 'en':
                                continue
                            tweets.append(tweet_content)
                            tweet_num += 1
        monthly_totals[date_dir] = tweet_num
        break
    break
                        
            
#print(json.dumps(tweets, indent=4))
#print(monthly_totals)

with open('2020-01-tweets.json', 'w', encoding='utf-8') as f:
    json.dump(tweets, f, ensure_ascii=False, indent=4)

# Save monthly totals dictionary
f2 = open("monthly_totals.pkl","wb")
pkl.dump(monthly_totals,f2)
f2.close()

c = Counter(x['user']['location'] for x in tweets)
location_totals = dict(c)
pp(location_totals)

# Save location totals dictionary
f3 = open("location_totals.pkl","wb")
pkl.dump(location_totals,f3)
f3.close()
            
        
        

      




