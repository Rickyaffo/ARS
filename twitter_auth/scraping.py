#! py -3
from twython import Twython , TwythonError, TwythonRateLimitError

import sys
import time
import csv
import networkx as nx
import math


def visit(nodes, node_central,threeshold):
    try:
        # visita del post in esame
        retweeters = follower_dict[node_central]
    except:
        pass
    for v, node in enumerate(nodes):
        try:
            retweeters_temp = follower_dict[node]
            find = True
            i = 0
            for t, e in enumerate(retweeters):
                if find:
                    for obj in retweeters_temp:
                        if (e == obj):
                            i += 1
                            if(i >= threeshold):
                                graph.add_edge(node_central, node)
                                find = False   #ho gia inserito l'edge
        except:
            pass

def handle_rate_limiting():
    while True:
        status = api.get_application_rate_limit_status(resources = ['statuses'])
        home_status = status['resources']['statuses']['/statuses/home_timeline']
        if home_status['remaining'] == 0:
            wait = max(home_status['reset'] - time.time(), 0) + 1 # addding 1 second pad
            time.sleep(wait)
        else:
            return
def make_graph(list_tweets):
    i = 0
    retweet_medio = tot / len(list_tweets)
  #  threeshold = math.sqrt(retweet_medio)
    threeshold = 4
    print("numero di retweet medio e valore threshold %s " % (retweet_medio))
    for i, v in enumerate(list_tweets):
        i = i + 1
        list_tweets2 = list_tweets[i:]
        # for t in list_tweets2:
        # print t
        # print("Start visit")
        visit(list_tweets2, v,threeshold)
    nx.write_graphml(graph, 'test6.graphml')
    print(nx.info(graph))

if __name__ == '__main__':
    # Consumer keys and access tokens, used for OAuthHandler
   

    api = Twython(API_KEY,
                  API_SECRET,
                  ACCESS_TOKEN,
                  ACCESS_TOKEN_SECRET)
    follower_dict = {}
    graph = nx.Graph()
    list_tweets = []
    tot = 0
    i = 0
    try:
        user_timeline = api.get_user_timeline(screen_name='TEDTalks', count=200)
    except TwythonError as e:
        print(e)
    print(len(user_timeline))
    try:
        for tweet in user_timeline:
            i = i + 1
            # Add whatever you want from the tweet, here we just add the text
            print(tweet['id'])
            handle_rate_limiting()
            retweeters = api.get_retweeters_ids(id = tweet['id'])  # utenti che hanno reetwettato
            users_linked = []
            if retweeters:  # se la lista non e' vuota aggiungi l'identificativo del tweet
                tot += len(retweeters)
                list_tweets.append(tweet['id'])
                graph.add_node(tweet['id'])
                for retweeter in retweeters['ids']:
                    users_linked.append(retweeter)
                follower_dict[tweet['id']] = users_linked  # inserisci la corrispondenza nel dizionario
        # Count could be less than 200, see:
        # https://dev.twitter.com/discussions/7513
    except TwythonRateLimitError as e:
        print("[Exception Raised] Rate limit exceeded")
        reset = int(api.get_lastfunction_header('x-rate-limit-reset'))
        wait = max(reset - time.time(), 0) + 10  # addding 10 second pad
        time.sleep(wait)
    except Exception as e:
        print(e)
        print("Non rate-limit exception encountered. Sleeping for 15 min before retrying")
        time.sleep(60 * 15)
    while len(user_timeline) != 0:
        try:
            print(i)
            users_linked = []
            handle_rate_limiting()
            user_timeline = api.get_user_timeline(screen_name='TEDTalks', count=200,
                                                      max_id=user_timeline[len(user_timeline) - 1]['id'] - 1)

            print(len(user_timeline))
            for tweet in user_timeline:
                i = i + 1
                # Add whatever you want from the tweet, here we just add the text
                handle_rate_limiting()
                retweeters = api.get_retweeters_ids(id = tweet['id'])  # utenti che hanno reetwettato
                users_linked = []
                if retweeters:  # se la lista non e' vuota aggiungi l'identificativo del tweet
                    tot += len(retweeters)
                    list_tweets.append(tweet['id'])
                    graph.add_node(tweet['id'])
                    for retweeter in retweeters['ids']:
                        users_linked.append(retweeter)
                    follower_dict[tweet['id']] = users_linked  # inserisci la corrispondenza nel dizionario
                    if i > 1200:
                        make_graph(list_tweets)
                        sys.exit()
        except TwythonRateLimitError as e:
            print("[Exception Raised] Rate limit exceeded")
            reset = int(api.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10  # addding 10 second pad
            time.sleep(wait)
        except Exception as e:
            print(e)
            print("Non rate-limit exception encountered. Sleeping for 15 min before retrying")
            time.sleep(60 * 15)


