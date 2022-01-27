# -*- coding: utf-8 -*-
"""
USA Hashtags Over Time
Megan M. Parsons | meganmp [at] bu [dot] edu
"""

# Imports
import csv
import emoji
import folium
from geopy.geocoders import Nominatim
import gzip
import json
import logging
import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle as pkl
import seaborn as sns
import unidecode
from fuzzywuzzy import fuzz
from collections import Counter
from collections import OrderedDict

matplotlib.use('Agg')

# Define directories
root_dir = '/analysis/'
save_dir = '/analysis/results/characterization/usa-tweets/' 

def main():
    
    # Set Seaborn theme
    sns.set_style('white')
    sns.set_context('paper')
    
    # Top keywords / hashtags
    with open(os.path.join(root_dir, 'usa_hashtags.pkl'), 'rb') as f:
        data = pkl.load(f)
        
    counted_hashtags = Counter(data)
    top_tags = []
    top_hashtags_usa = counted_hashtags.most_common(15)
    for x in top_hashtags_usa:
        y = x[0]
        y = y.lower()
        if 'covid' not in y and 'coronavirus' not in y:
            top_tags.append([x[0], x[1]])
            
    # Keyword Diagram
    df = pd.DataFrame(top_tags, columns = ['Hashtag', 'Count'])
    sns.set(font_scale = 2.7)
    
    plt.figure()
    plt.figure(figsize=(44,24))
    sns.barplot(data = df, y='Hashtag', x='Count').set(title='Top COVID-19 Hashtags in USA from Jan-Jun 2020')
    plt.savefig(save_dir + '/usa_top_hashtags.jpg')
   
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()

