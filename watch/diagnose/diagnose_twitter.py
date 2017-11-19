import json
import requests
import csv
import os
import tweepy
import indicoio
from indicoio.utils.errors import IndicoError
indicoio.config.api_key = '83a12f4a1870089de3e02f0b4ec3aa47'

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
    
    content = response.content.decode('utf-8').replace("'", '"')
    response = json.loads(content)
    
    return response['documents']


def measure_emotion_batch(documents):
    max_sad = 0
    sad_id = ""
    for doc in documents:
        try:
            doc['emotions'] = indicoio.emotion(doc['text'])
            if max_sad < doc['emotions']['sadness']:
                max_sad = doc['emotions']['sadness']
                sad_id = doc['id']
        except IndicoError:
            doc['emotions'] = {
                'anger': 0., 
                'joy': 0.,
                'sadness': 0., 
                'fear': 0., 
                'surprise': 0.
            }

    return documents, sad_id


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
    print("sending dm to:", username)
    if message == None:
        message = "Someone cares about you. If you're feeling down, call 1-800-273-8255. If you're okay, let someone else know you care by visiting bit.do/whenwl."

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
            if emotion > EMOTION_THRESH:
                output[tid] = res['score'] * (1 + emotion)
                if output[tid] > 1:
                    output[tid] = 1
            else:
                output[tid] = 0
        else:
            output[tid] = 0

    return output

def diagnose_twitter(username):
    # Get user's tweets and measure sentiments
    # test_users = [
    #     "djkhaled",
    #     "iDepressing",
    #     "HarshBuddy98",
    #     "xxxtentacion",
    #     "Freddy_E",
    #     "fmahbouba",
    #     "asahdkhaled"
    # ]
    # user_tweets = tweets_from_user(test_users[-1])

    user_tweets = tweets_from_user(username)
    if len(user_tweets) < 1:
        return -1

    documents = format_tweets_to_documents(user_tweets)
    sentiments = measure_sentiment_batch(documents)
    emotions, sad_id = measure_emotion_batch(documents)

    results = {}
    for sent in sentiments:
        results[sent['id']] = {'score': sent['score']}

    for emo in emotions:
        results[emo['id']]['emotions'] = emo['emotions']
        results[emo['id']]['text'] = emo['text']

    results_modified = score_model(results)

    scores = []
    for tid, res in results.items():
        scores.append(results_modified[tid])
        # print("{}: {}: {}".format(tid, res['score'], results_modified[tid]))

    # print("Average Score:{}".format(average_score(scores)))
    return average_score(scores), results[sad_id]['text']

def generate_message(score):
    if score < 10:
        return "We believe it is extremely crucial that you check up on this individual as they definitely need someone to be there for them."
    elif score < 20:
        return "There is a definite concern with this individual’s mental health and it would be advised you check up on them if possible."
    elif score < 30:
        return "The individual you have searched for needs to be checked up on as they seem to be battling some type of mental distress."
    elif score < 40:
        return "This individual may be going through a rough time and it would not hurt to check up on them."
    elif score < 50:
        return "While there is no definite reason to check up, just make sure you do say hi next time you see them to make sure they’re okay."
    elif score < 60:
        return "While this is an average result, it never hurts to check up on them."
    elif score < 70:
        return "Do not worry, they’re doing perfectly fine."
    elif score < 80:
        return "While they aren’t perfect, they’re still enjoying life."
    elif score < 100:
        return "These people are loving life, there’s no reason to worry about their mental state."
    else:
        return "Error, invalid score"
