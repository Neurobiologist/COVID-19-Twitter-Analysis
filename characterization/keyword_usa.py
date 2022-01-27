# -*- coding: utf-8 -*-
"""
COVID-19 USA Keywords
Megan M. Parsons | meganmp [at] bu [dot] edu
"""

# Imports
import gzip
import json
import logging
import os
from collections import OrderedDict

# Define directories
root_dir = '/data/usa-tweets/'
save_dir = '/analysis/results/characterization/usa-tweets/' 

def rank_locations(loc_dict):
    ''' Return top 100 locations from location dictionary'''
    loc_dict = OrderedDict(sorted(loc_dict.items(), key=lambda x: x[1], reverse=True))
    first_n_values = list(loc_dict.items())[:100]
    return first_n_values


def main():
    
    keyword_dict = dict()
    
    # Traverse the data
    for sub_dir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for date_dir in sorted(dirs):
            logging.info('Processing %s', date_dir)
            tweet_num = 0
            for file in sorted(os.listdir(os.path.join(root_dir, date_dir))):
                file_extension = os.path.splitext(file)[1]
                if file_extension == '.gz':
                    logging.info('Processing %s', file)
                    with open(os.path.join(sub_dir, date_dir, file), 'rb') as f:
                       gzip_f = gzip.GzipFile(fileobj=f)
                       orig_df = pd.read_json(gzip_f, lines=True)
                        
        
                    # Drop extraneous information    
                    orig_df = orig_df.drop('id_str', 1)
                    orig_df = orig_df.drop('contributors', 1)
                    orig_df = orig_df.drop('possibly_sensitive', 1)
                    orig_df = orig_df.drop('lang', 1)
                    orig_df = orig_df.drop('display_text_range', 1)
                    orig_df = orig_df.drop('source', 1)
                    orig_df = orig_df.drop('quoted_status_permalink',1)
                    
                    # Restructure dataframe
                    tweet_df = pd.DataFrame(columns = ['created_at', 'id', 'user_id',
                                                       'tweet_text', 'hashtags', 
                                                       'user_followers_count',
                                                       'is_reply',
                                                       'in_reply_to_status_id',
                                                       'in_reply_to_user_id',
                                                       'in_reply_to_screen_name',
                                                       'is_retweet',
                                                       'retweeted_id',
                                                       'retweeted_screen_name',
                                                       'has_mentions',
                                                       'user_mention_id',
                                                       'user_mention_screen_name',
                                                       'is_geo',
                                                       'geo_coordinates',
                                                       'is_profile_loc',
                                                       'profile_loc'
                                                       ])
                    
                    # Direct transfer of information
                    transfer_cols = ['created_at', 'id', 'in_reply_to_status_id', 'in_reply_to_user_id',
                                     'in_reply_to_screen_name']
                    tweet_df[transfer_cols] = orig_df[transfer_cols]
                    
                    # Format remaining information
                    tweet_df['hashtags'] = orig_df['entities'].apply(lambda x: [y['text'] for y in x['hashtags']])
                    tweet_df['is_reply'] = orig_df['in_reply_to_screen_name'].apply(lambda x: False if x == None else True)
                    tweet_df['is_retweet'] = orig_df['retweeted_status'].apply(lambda x: is_retweet(x))
                    
                    
                    for index, row in orig_df.iterrows():
                        
                        # User ID
                        if orig_df.loc[index, 'user']['id_str'] == None:
                            tweet_df.loc[index, 'user_id'] = None
                        else:
                            tweet_df.loc[index, 'user_id'] = orig_df.loc[index, 'user']['id_str']
                            tweet_df.loc[index, 'user_name'] = orig_df.loc[index, 'user']['screen_name']
                            tweet_df.loc[index, 'user_followers_count'] = orig_df.loc[index, 'user']['followers_count']
                        
                        # User Mentions
                        if not orig_df.loc[index, 'entities']['user_mentions']:
                            tweet_df.loc[index, 'has_mentions'] = False
                        else:
                            tweet_df.loc[index, 'has_mentions'] = True
                            tweet_df.loc[index, 'user_mention_id'] = orig_df.loc[index, 'entities']['user_mentions'][0]['id']
                            tweet_df.loc[index, 'user_mention_screen_name'] = orig_df.loc[index, 'entities']['user_mentions'][0]['screen_name']
                        
                        # Capture full text of tweet
                        if is_retweet(orig_df.loc[index, 'retweeted_status']):
                            tweet_df.loc[index, 'tweet_text'] = preprocess_retweet(row['retweeted_status'])
                            tweet_df.loc[index, 'retweeted_id'] = orig_df.loc[index, 'retweeted_status']['user']['id_str']
                            tweet_df.loc[index, 'retweeted_screen_name'] = orig_df.loc[index, 'retweeted_status']['user']['screen_name']
                        else:
                            try:
                                tweet_df.loc[index, 'tweet_text'] = preprocess_ext_tweet(row['extended_tweet'])
                            except:
                                tweet_df.loc[index, 'tweet_text'] =  row['full_text']
                                
                        # Geotagging
                        if orig_df.loc[index, 'geo'] == None:
                            tweet_df.loc[index, 'is_geo'] = False
                            tweet_df.loc[index, 'geo_coordinates'] = None
                        else:
                            try:
                                tweet_df.loc[index, 'geo_coordinates'] = orig_df.loc[index, 'geo']['coordinates']
                                tweet_df.loc[index, 'is_geo'] = True
                            except:
                                tweet_df.loc[index, 'is_geo'] = False
                                tweet_df.loc[index, 'geo_coordinates'] = None
                                
                        # User Location
                        if orig_df.loc[index, 'user']['location'] == None or type(orig_df.loc[index, 'user']['location']) != str:
                            tweet_df.loc[index, 'is_profile_loc'] = False
                            tweet_df.loc[index, 'profile_loc'] = None
                        else:
                            tweet_df.loc[index, 'is_profile_loc'] = True
                            tweet_df.loc[index, 'profile_loc'] = orig_df.loc[index, 'user']['location']
                                
                    logging.info('ORGANIZING DATA COMPLETE')
                    
                    # Save pkl file
                    tweet_df.save_pickle('usa_tweets_df.pkl')                    

                        except:
                            continue

            monthly_totals[date_dir] = tweet_num
            logging.info('Monthly Total: %s\t%d', date_dir, tweet_num)
                
    logging.info('TRAVERSING DATA COMPLETE')
    
    # Save monthly totals dictionary
    logging.info('Saving monthly totals')
    with open(os.path.join(save_dir, 'monthly_totals-usa.json'), 'w', encoding='utf-8') as f:
        json.dump(monthly_totals, f, ensure_ascii=False, indent=4)
        
    # Save language totals dictionary
    logging.info('Saving language totals')
    with open(os.path.join(save_dir, 'language_totals-usa.json'), 'w') as f2:
        json.dump(language_totals, f2)  
        
    logging.info('Processing Complete')


if __name__ == "__main__":
    main()
           
