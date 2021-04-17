# -*- coding: utf-8 -*-
"""
COVID-19 Twitter Analysis
Megan M. Parsons | meganmp@bu.edu
INSTRUCTIONS: To run, type into terminal: ./preprocessing.py >> out.txt 
"""

# Imports
from collections import Counter
import gzip
import json
import jsonlines
import os
from pprint import pprint as pp

# Define directories
root_dir = '/projectnb/caad/meganmp/data/COVID-19-TweetIDs-master'	# Testing: '/projectnb/caad/meganmp/data/data-subset/' | Analysis: 
save_dir = '/projectnb/caad/meganmp/data/english-tweets' 

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
                with gzip.open(os.path.join(save_dir, date_dir, file), 'w') as file_out:
                    with gzip.open(os.path.join(sub_dir, date_dir, file), 'r') as gzip_file:
                        for line in gzip_file:
                            line = line.rstrip()
                            if line:
                                tweet_content = json.loads(line)
                                if tweet_content['lang'] == 'en':	# Filter out non-English Tweets
                                    file_out.write(line + b'\n')
                                    #tweets.append(tweet_content)
                                    tweet_num += 1
                
        monthly_totals[date_dir] = tweet_num
        print(monthly_totals)
        #break
    print('--------------- NEXT DATE DIRECTORY ---------------------')
    #break
                        
            
#print(json.dumps(tweets, indent=4))
#print(monthly_totals)
print('TRAVERSING DATA COMPLETE')

# Save monthly totals dictionary
print('Saving monthly totals')
with open('/projectnb/caad/meganmp/analysis/monthly_totals-english.json', 'w', encoding='utf-8') as f:
    json.dump(monthly_totals, f, ensure_ascii=False, indent=4)

print('Initializing Counter')
c = Counter(x['user']['location'] for x in tweets)
print('Counter Complete')
location_totals = dict(c)
print('Counter converted to dictionary')
pp(location_totals)

# Save location totals dictionary
print('Saving location totals')
with open('/projectnb/caad/meganmp/analysis/location_totals-english.json', 'w') as f2:
    json.dump(location_totals, f2)

print('Preprocessing Complete')
            
        
        

      




