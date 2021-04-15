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

tweet_json = '/projectnb/caad/meganmp/data/english-tweets/2020-01/coronavirus-tweet-id-2020-01-31-22.jsonl.gz'
with gzip.open(tweet_json, 'r') as gzip_file:
    for line in gzip_file:
        line = line.rstrip()
        if line:
            print(line)
            tweet = json.loads(line)
            resolver = carmen.get_resolver()
            resolver.load_locations()
            location = resolver.resolve_tweet(tweet)
            print(location)
