import datetime
import json
import requests
import csv
import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks")
import pandas as pd
import tweepy
import indicoio
indicoio.config.api_key = '1c7243947462c66f46ef617aadee4197'

# Twitter
OWNER_ID = "2225496692"
CONSUMER_KEY = "NMCgbXWeDTBH81AWfLHcsrUFD"
CONSUMER_SECRET = "IOchHeHiaXgY4Nc9FNCnoqsz50c7iroBufkq2IqKbcKzhBjrdv"
ACCESS_TOKEN = "2225496692-rRh9c5CQGdMPEhktkymBBzPnWNaWe8CPb0MtOns"
ACCESS_TOKEN_SECRET = "TNHWtxYQetMV9xOtfWS4CURZQUxxbhEXrfasT5a19p84a"
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Microsoft
MICROSOFT_API = "https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
MICROSOFT_KEY1 = "5a132f37774448d1bc7cb9196663d74d"
MICROSOFT_KEY2 = "e3419c68c67b4b84aa33086c3200e060"

def GetSentiment (documents):
   "Gets the sentiments for a set of documents and returns the information."
   
   
 
def emotion_count(username):
    history = []

    count = {
        'anger': 0., 
        'joy': 0.,
        'sadness': 0., 
        'fear': 0., 
        'surprise': 0.
    }

    user_tweets = api.user_timeline(username, count=50)
    counter = 0
    for tweet in user_tweets:
        print(tweet.text)
        print(tweet.retweeted)
        if 'http' in tweet.text:
            continue
        emotions = indicoio.emotion(tweet.text)
        for key, value in count.items():
            count[key] += emotions[key]
        history.append({'index': counter, 'sadness': emotions['sadness']})
        # history.append({'date': tweet.created_at, 'sadness': emotions['sadness']})
        # print(indicoio.emotion(tweet.text))
        print()
        counter += 1
    print(count)

    print(history)
    df = pd.DataFrame(history)

    print(df)
    ax = sns.regplot(x="index", y="sadness", data=df)
    plt.show()

def tweets_from_search(search):
    user_tweets = api.search(search, rpp=100)

    filename = 'tweets.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['tweetID', 'tweet', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()

        for tweet in user_tweets:
            if "RT" not in tweet.text:
                writer.writerow({'tweetID': tweet.id_str, 'tweet': tweet.text, 'rating': 0})

def tweets_from_user(username, pages=3):
    for page in range(pages):
        user_tweets = api.user_timeline(username, count=200, page=page)
        filename = 'tweets.csv'
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['tweetID', 'tweet', 'rating']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()

            for tweet in user_tweets:
                if "RT" not in tweet.text:
                    writer.writerow({'tweetID': tweet.id_str, 'tweet': tweet.text, 'rating': 0})

def send_response_dm(username, message=None):
    if message == None:
        message = "Someone cares about you. If you're feeling down, call 1-800-273-8255."

    api.send_direct_message(username, text=message)


if __name__ == '__main__':

    headers = {
        'Ocp-Apim-Subscription-Key': MICROSOFT_KEY1, 
        'Content-Type': 'application/json', 
        'Accept': 'Content-Type'
    }

    documents = {
        'documents': [
            { 'id': '1', 'text': 'I really enjoy the new XBox One S. It has a clean look, it has 4K/HDR resolution and it is affordable.'}
        ]
    }

    response = requests.post(MICROSOFT_API, data=json.dumps(documents), headers=headers)
    response = json.loads(response.content)
    print(response['documents'][0]['score'])
        







    # print (json.dumps(json.loads(result), indent=4))


    # emotion_count("alimalik32")
    # emotion_count("Freddy_E")
    # emotion_count("amandatodd101")

    """
    I’m Sorry.
    Forgive me.
    Sorry
    Hate
    Im done with my life
    I cant take this anymore
    Can’t 
    Suffering
    Why is this happening?
    Kill myself
    Struggle
    You will miss me
    Forgotten
    Betrayed
    Withdrawn
    Alone
    Lonely
    Tired 
    Burden 
    Weakness
    No desire
    No energy
    Nobody notices me
    Nobody cares
    I tried
    """

    # tweets_from_search('im sorry')
    # tweets_from_search('forgive')
    # tweets_from_search('betrayal')
    # tweets_from_search('me')
    # tweets_from_search('i cant')
    # tweets_from_search('horrible')
    # tweets_from_search('sad')
    # tweets_from_search('your everything')
    # tweets_from_search('done with life')
    # tweets_from_search('its over')
    # tweets_from_search('forgotten')
    # tweets_from_search('suffering')
    # tweets_from_search('kill myself')
    # tweets_from_search('end it')
    # tweets_from_search('struggle')
    # tweets_from_search('you will miss me')
    # tweets_from_search('tired')
    # tweets_from_search('lonely')
    # tweets_from_search('no desire')
    # tweets_from_search('i tried')
    # tweets_from_search('alone')
    # tweets_from_search('no one')
    # tweets_from_search('no one understands')
    # tweets_from_search('lost')
    # tweets_from_search('weak')
    # tweets_from_search('just burden')
    # tweets_from_search('abused')


    # tweets_from_user('depressingmsgs', pages=20)
    # tweets_from_user('idepressing', pages=20)

    # used_ids = []
    # alltweets = []
    # cnt = 0
    # with open('tweets.csv', newline='') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         tweetID = row['tweetID']
    #         if row['tweetID'] not in used_ids:
    #             used_ids.append(tweetID)
    #             alltweets.append({'tweetID': tweetID, 'tweet': row['tweet'], 'rating': 0})
    #             cnt+=1
    #             print(cnt)

    # with open('tweets_new.csv', 'w', newline='') as csvfile:
    #         fieldnames = ['tweetID', 'tweet', 'rating']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
    #         writer.writeheader()

    #         for tweet in alltweets:
    #             if "RT" not in tweet['tweet']:
    #                 writer.writerow(tweet)