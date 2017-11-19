import json
import requests
import csv
import os
import tweepy
import indicoio
from indicoio.utils.errors import IndicoError
indicoio.config.api_key = '1c7243947462c66f46ef617aadee4197'

# Twitter
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

def measure_sentiment_batch(documents):
    """
    Gets the sentiments for a set of documents and returns the information.
    documents - list of documents ready to be analyzed
    """

    headers = {
        'Ocp-Apim-Subscription-Key': MICROSOFT_KEY1, 
        'Content-Type': 'application/json', 
        'Accept': 'Content-Type'
    }

    # Sample data
    # data = {
    #     'documents': [
    #         { 'id': '1', 'text': 'I really hate the new XBox One S.'},
    #         { 'id': '2', 'text': 'I really enjoy the new XBox One S. It has a clean look, it has 4K/HDR resolution and it is affordable.'}
    #     ]
    # }

    data = json.dumps({'documents': documents})
    response = requests.post(MICROSOFT_API, data=data, headers=headers)
    response = json.loads(response.content)
    
    return response['documents']


def measure_emotion_batch(documents):
    for doc in documents:
        print(doc['text'])
        try:
            doc['emotions'] = indicoio.emotion(doc['text'])
        except IndicoError:
            doc['emotions'] = {
                'anger': 0., 
                'joy': 0.,
                'sadness': 0., 
                'fear': 0., 
                'surprise': 0.
            }

    return documents


def format_tweets_to_documents(tweets):
    """
    Format tweets as documents to be sent to Microsoft Sentiment Analysis and make sure ids are not repeated.
    """

    used_ids = []
    documents = []
    for tweet in tweets:
        if (tweet.id_str not in used_ids) and ("RT" not in tweet.text):
            used_ids.append(tweet.id_str)
            documents.append({'id': tweet.id_str, 'text': tweet.text})

    return documents


def tweets_from_user(username, count=100, pages=1):
    user_tweets = []
    for page in range(pages):
        user_tweets.extend(api.user_timeline(username, count=count, page=page))

    return user_tweets


def send_response_dm(username, message=None):
    if message == None:
        message = "Someone cares about you. If you're feeling down, call 1-800-273-8255."

    api.send_direct_message(username, text=message)


def average_score(scores):
    total = 0
    count = 0
    for score in scores:
        if score != 0:
            count += 1
            total += score
    return total/count


def score_model(results):
    EMOTION_THRESH = 0.1

    output = {}
    for tid, res in results.items():
        score = res['score']
        print("Score is " + str(score))
        if score < 0.5:
            output[tid] = res['score']
            # emotion = (res['emotions']['fear']*res['emotions']['sadness'])/2
            # print("Emotion is " + str(emotion))
            # if emotion > EMOTION_THRESH:
            #     output[tid] = res['score'] * (1 - emotion)
            # else:
            #     output[tid] = 0
        elif score > 0.5:
            emotion = res['emotions']['joy']
            print("Emotions is " + str(emotion))
            if emotion > EMOTION_THRESH:
                output[tid] = res['score'] * (1 + emotion)
                if output[tid] > 1:
                    output[tid] = 1
            else:
                output[tid] = 0
        else:
            output[tid] = 0

    return output


if __name__ == '__main__':
    # Get user's tweets and measure sentiments
    test_users = [
        "djkhaled",
        "iDepressing",
        "HarshBuddy98",
        "xxxtentacion",
        "Freddy_E"
    ]
    user_tweets = tweets_from_user(test_users[3])
    documents = format_tweets_to_documents(user_tweets)
    sentiments = measure_sentiment_batch(documents)
    emotions = measure_emotion_batch(documents)

    results = {}
    for sent in sentiments:
        results[sent['id']] = {'score': sent['score']}

    for emo in emotions:
        results[emo['id']]['emotions'] = emo['emotions']

    results_modified = score_model(results)

    scores = []
    for tid, res in results.items():
        scores.append(results_modified[tid])
        # print("{}: {}: {}".format(tid, res['score'], results_modified[tid]))

    print("Average Score:{}".format(average_score(scores)))

