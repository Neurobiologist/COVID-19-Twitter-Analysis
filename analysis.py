# -*- coding: utf-8 -*-
"""
COVID-19 Twitter Analysis
Megan M. Parsons | meganmp@bu.edu
"""

# Imports
import gzip
import json
import os
import pandas as pd

# Test file access
root_dir = '/projectnb/caad/meganmp/COVID-19-TweetIDs-master/'

for sub_dir, dirs, files in os.walk(root_dir):
    dirs.sort()
    files.sort()
    for date_dir in sorted(dirs):
        print(date_dir)
    for file in sorted(files):
        print(os.path.join(subdir, file))
        
        

      
tweets = []
i = 0
with gzip.open(filename, 'rb') as gzip_file:
    for line in gzip_file:
        line = line.rstrip()
        if line:
            tweet_content = json.loads(line)
            tweets.append(tweet_content)
            i += 1
            
print(json.dumps(tweets, indent=4))
print(i)



