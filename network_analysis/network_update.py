# Imports
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

# Pandas Settings
pd.set_option('max_colwidth', 280)  # Capture full tweet
pd.set_option("display.max_rows", None, "display.max_columns", None)

def get_interactions(row):
    '''Build Interactions for Network'''
     
    # Define interactions
    interactions = set()
    
    # Replies
    interactions.add((str(row["in_reply_to_user_id"]), str(row["in_reply_to_screen_name"])))
    # Retweets
    #interactions.add((str(row["retweeted_id"]), str(row["retweeted_screen_name"])))
    # User Mentions
    #interactions.add((str(row["user_mention_id"]), str(row["user_mention_screen_name"])))
    
    # Discard user
    interactions.discard(row["user_id"])
    
    # Discard all None/NaN interactions
    interactions.discard(('None', 'None'))
    interactions.discard(('None', 'nan'))
    interactions.discard(('nan', 'None'))
    interactions.discard(('nan', 'nan'))

    return [row['user_id'], row['user_name']], interactions

def main():
	# Load pkl file
    tweet_df = pd.read_pickle('usa_tweets_df.pkl')
    
    # Build Network Graph
    network = nx.Graph()
    
    for index, row in tweet_df.iterrows():
        user, interactions = get_interactions(row)
        user_id = user[0]
        user_name = user[1]
        tweet_id = row["id"]
        for interaction in interactions:
            int_id, int_name = interaction
            network.add_edge(user_id, int_id, tweet_id=tweet_id)
            network.nodes[user_id]["name"] = user_name
            network.nodes[int_id]["name"] = int_name
               
    # Identify largest subnetwork
    subnetwork = network.subgraph(max(nx.connected_components(network), key=len))
    
    # Calculate degrees of each node
    degrees = [deg for (node, deg) in network.degree()]
    sub_degrees = [deg for (node, deg) in subnetwork.degree()]
            
    with open('network_analysis-expanded-update-noRTorUM.txt', 'w') as file_out:
        file_out.write('Nodes = {}\n'.format(network.number_of_nodes()))
        file_out.write('Edges = {}\n'.format(network.number_of_edges()))
        file_out.write('Max Degree = {}\n'.format(np.max(degrees)))
        file_out.write('Average degree = {}\n'.format(np.mean(degrees)))
        file_out.write('Most frequent degree = {}\n'.format(stats.mode(degrees)[0][0]))
        file_out.write('# Connected Components = {}\n'.format(nx.number_connected_components(network)))
    
        if nx.is_connected(network):
            file_out.write('Network is connected.\n')
        else:
            file_out.write('Network not connected.\n')
        
        file_out.write('\nLargest Subgraph Analysis\n')
        file_out.write('Nodes = {}\n'.format(subnetwork.number_of_nodes()))
        file_out.write('Edges = {}\n'.format(subnetwork.number_of_edges()))
        file_out.write('Max Degree = {}\n'.format(np.max(sub_degrees)))
        file_out.write('Average degree = {}\n'.format(np.mean(sub_degrees)))
        file_out.write('Most frequent degree = {}\n'.format(stats.mode(sub_degrees)[0][0]))
        file_out.write('# Connected Components = {}\n'.format(nx.number_connected_components(subnetwork)))
    

    plt.figure(figsize=(50,50))
    nx.draw(network)
    plt.savefig('network-usa-update-noRToruM.jpg')
    
    plt.figure(figsize=(50,50))
    nx.draw(subnetwork)
    plt.savefig('subnetwork-usa-update-noRToruM.jpg')

if __name__ == "__main__":
    main()
           