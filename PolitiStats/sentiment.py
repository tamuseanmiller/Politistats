from PolitiStats.api import user_tweets, get_news, work, search_tweets_timeline, get_news_timeline
from google.cloud import language_v1

client = language_v1.LanguageServiceClient()


# prints tweets and runs sentiment analysis on mentions by timeline
def gather_mentions_timeline(politician_handle):

    # Error Handling
    if politician_handle == "":
        return float('nan')
    timeline = []
    documents = []

    # Fetch tweets and loop
    week = search_tweets_timeline(politician_handle)
    for tweets in week:

        for tweet in tweets:

            # Check to make sure there is text in tweet
            if tweet is not None:
                documents.append(tweet)

        # Run sentiment analysis on tweets
        sentiment = run_sentiment_google(documents)
        documents.clear()
        if len(documents) != 0:
            sentiment /= len(documents)
        timeline.append(round(sentiment, 2))

    return timeline[::-1]


# Get last 7 articles
def gather_news_timeline(politician_name):
    timelines = []

    # Get last weeks news articles
    week = get_news_timeline(politician_name)
    for day in week:
        sentiment = 0

        # Make sure there is a news article for that day
        if len(day) > 0:
            sentiment += run_sentiment_google(day)
            sentiment /= len(day)

        timelines.append(round(sentiment, 2))
    return timelines[::-1]


# prints tweets and runs sentiment analysis on mentions
def gather_sentiment_mentions(politician_handle):

    # Error handling
    if politician_handle == "":
        return float('nan')

    # Grab all mentions towards poltician on Twitter
    tweets = work(politician_handle)
    documents = []

    # Loop through tweets and add to documents
    for i in range(0, len(tweets)):
        if tweets[i]['Text'] is not None:
            documents.append(tweets[i]['Text'])

    # Run sentiment on list of tweets and find mean
    sentiment = run_sentiment_google(documents)
    if len(tweets) != 0:
        sentiment /= len(tweets)

    return round(sentiment, 2)


# prints news and runs sentiment analysis on a query
def gather_sentiment_news(politician_name):
    ret = get_news(politician_name)
    documents = []
    for i in range(0, len(ret)):
        if i is not None:
            documents.append(ret[i]['Content'])

    sentiment = run_sentiment_google(documents)

    if len(ret) != 0:
        sentiment /= len(ret)
    return round(sentiment, 2), ret


# Prints tweets and runs sentiment analysis from handle
def gather_sentiment_tweets(politician_handle):

    # Error handling
    if politician_handle == "":
        return float('nan')

    # Gets tweets that politician has made
    tweets = []
    ret = user_tweets(politician_handle)

    # Loop through tweets and appends them to a list
    for i in range(0, len(ret)):
        tweets.append(ret[i]['Text'])

    # Finds sentiment in list of tweets, then average it
    sentiment = run_sentiment_google(tweets)
    if len(ret) != 0:
        sentiment /= len(ret)
    return round(sentiment, 2)


def run_sentiment_google(sentences):
    sentiment = 0
    for sentence in sentences:
        document = language_v1.types.Document(content=sentence, type_=language_v1.Document.Type.PLAIN_TEXT)

        # Detects the sentiment of the text
        response = client.analyze_sentiment(document=document)

        sentiment += response.document_sentiment.score
    return sentiment


# print(gather_sentiment_tweets("KamalaHarris"))
# print(gather_mentions_timeline("realDonaldTrump"))
# print(gather_sentiment_mentions("realDonaldTrump"))
# print(gather_sentiment_news("Joe Biden"))
# print(gather_news_timeline("Kamala Harris"))
