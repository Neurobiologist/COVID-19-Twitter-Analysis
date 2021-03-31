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
import pandas as pd
import pickle as pkl
from pprint import pprint as pp

# Test file access
root_dir = '/projectnb/caad/meganmp/COVID-19-TweetIDs-master/2020-01/'
monthly_totals = dict()

for sub_dir, dirs, files in os.walk(root_dir):
    dirs.sort()
    files.sort()
    for date_dir in sorted(dirs):
        print(date_dir)
    for file in sorted(files):
        file_extension = os.path.splitext(file)[1]
        if file_extension == '.gz':
            print(file)
            tweets = []
            tweet_num = 0
            with gzip.open(os.path.join(sub_dir,file), 'rb') as gzip_file:
                for line in gzip_file:
                    line = line.rstrip()
                    if line:
                        tweet_content = json.loads(line)
                        tweets.append(tweet_content)
                        tweet_num += 1
                monthly_totals[date_dir] = tweet_num
                        
            
print(json.dumps(tweets, indent=4))
print(monthly_totals)

# Save monthly totals dictionary
f = open("monthly_totals.pkl","wb")
pkl.dump(monthly_totals,f)
f.close()

c = Counter(x['user']['location'] for x in tweets)
location_totals = dict(c)
pp(location_totals)

# Save location totals dictionary
f2 = open("location_totals.pkl","wb")
pkl.dump(location_totals,f2)
f2.close()
            
        
        

      




