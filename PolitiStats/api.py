import re

import requests
import tweepy
import ssl
import time

from botocore.exceptions import ReadTimeoutError
from requests.exceptions import Timeout, ConnectionError
import datetime

from PolitiStats.properties import getConsumerKey, getCivicsKey, getConsumerSecret, getAccessKey, getAccessSecret, \
    getNewsKey


def getStateOfficials(state):
    request = requests.get(
        "https://civicinfo.googleapis.com/civicinfo/v2/representatives/ocd-division%2Fcountry%3Aus%2Fstate%3A" +
        state + "?key=" + getCivicsKey())

    civics_data = request.json()
    offices = []
    officials = []
    for i in range(0, len(civics_data['offices'])):
        offices.append(civics_data['offices'][i]['name'])

        try:
            official = {
                "office": civics_data['offices'][i]['name'],
                "name": civics_data['officials'][i]['name'],
                "party": civics_data['officials'][i]['party'],
                "socials": civics_data['officials'][i]['channels']
            }
            officials.append(official)
        except:
            official = {
                "office": civics_data['offices'][i]['name'],
                "name": civics_data['officials'][i]['name'],
                "party": civics_data['officials'][i]['party'],
                "socials": "null"
            }
            officials.append(official)

        # print()
    return officials


def clean_tweets(content):
    """Convert all named and numeric character references
                (e.g. &gt;, &#62;, &#x3e;) in the string s to the
                corresponding Unicode characters"""
    content = (content.replace('&amp;', '&').replace('&lt;', '<')
               .replace('&gt;', '>').replace('&quot;', '"')
               .replace('&#39;', "'").replace(';', " ")
               .replace(r'\u', " ").replace('\u2026', "")
               .replace('\n', ''))

    content.encode('ascii', 'ignore').decode('ascii')

    # Exclude retweets, too many mentions and too many hashtags, and remove handles and hashtags
    if not any((('RT @' in content, 'RT' in content,
                 content.count('@') >= 3, content.count('#') >= 3))):
        content = re.sub('@[^\s]+', '', content)
        content = re.sub('#[^\s]+', '', content)

        return content
    return None


# Handling authentication with Twitter
auth = tweepy.OAuthHandler(getConsumerKey(), getConsumerSecret())
auth.set_access_token(getAccessKey(), getAccessSecret())

# Create a wrapper for the API provided by Twitter
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# Function for handling pagination in our search
def limit_handled(cursor):
    while True:
        try:
            try:
                yield cursor.next()
            except StopIteration:
                return
        except tweepy.RateLimitError:
            print('Reached rate limit. Sleeping for >15 minutes')
            time.sleep(15 * 61)


# Function to make the search using Twitter API for 7 days of data
def search_tweets_timeline(official_handle):
    timeline = []
    for i in range(0, 7):

        tweets = []

        # Finds the tweets from cursor and iterates through
        for tweet in limit_handled(tweepy.Cursor(api.search,
                                                 q="@" + official_handle,
                                                 count=20,
                                                 tweet_mode='extended',
                                                 lang="en",
                                                 result_type='recent',
                                                 until=datetime.date.today() - datetime.timedelta(days=i)).items(20)):

            try:

                # Checks if its an extended tweet (>140 characters)
                content = tweet.full_text
                content = clean_tweets(content)
                if content is not None:
                    tweets.append(content)

            except Exception as e:
                print('Encountered Exception:', e)
                pass
        timeline.append(tweets)
    return timeline


# Fetches url for image of official and description
def get_official_info(official_name):
    # queries wikipedia to find the title of article
    title = requests.get(
        "https://en.wikipedia.org/w/api.php?action=opensearch&search=" + official_name.replace(' ',
                                                                                               '') + "&limit=1&namespace=0&format=json")

    # Fetches the main image based on the title
    image = requests.get("http://en.wikipedia.org/w/api.php?action=query&titles="
                         + title.json()[3][0][30:] + "&prop=pageimages&format=json&pithumbsize=100")

    # Fetches short description of politician
    description = requests.get(
        "https://en.wikipedia.org/w/api.php?format=json&action=query"
        "&prop=extracts&exintro&explaintext&redirects=1&titles=" +
        title.json()[3][0][30:])

    # Get larger image than thumbnail
    try:
        image_src = str(list(image.json()['query']['pages'].items())[0][1]['thumbnail']['source'])
        index = image_src.find("px")
        image_src = image_src.replace(image_src[index - 2:], "512" + image_src[index:])

    # If no image exists in wikipedia
    except:
        image_src = "https://images.unsplash.com/photo-1547354142-526457358bb7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=80"

    try:
        desc_src = list(description.json()['query']['pages'].items())[0][1]['extract']

    except:
        desc_src = "No description exists..."

    # returns a dictionary with description and image
    info = {"Image": image_src,
            "Description": desc_src}

    # Returns the actual image
    return info


# Function to make the search using Twitter API
def search_tweets(official_handle):
    tweets = []

    # Finds the tweets from cursor and iterates through
    for tweet in limit_handled(tweepy.Cursor(api.search,
                                             q="@" + official_handle,
                                             count=20,
                                             tweet_mode='extended',
                                             lang="en",
                                             result_type='popular',
                                             until=datetime.date.today()).items(20)):

        try:
            # Checks if its an extended tweet (>140 characters)
            content = tweet.full_text

            if content is not None:
                tweets.append({"Text": content,
                               "Day": int(tweet.created_at.day)})

        except Exception as e:
            print('Encountered Exception:', e)
            pass

    return tweets


def work(official_handle):
    # Initializing the Twitter search
    tweets = []
    try:
        tweets = search_tweets(official_handle)

    # Stop temporarily when hitting Twitter rate Limit
    except tweepy.RateLimitError:
        print("RateLimitError...waiting ~15 minutes to continue")
        time.sleep(1001)
        search_tweets(official_handle)

    # Stop temporarily when getting a timeout or connection error
    except (Timeout, ssl.SSLError, ReadTimeoutError,
            ConnectionError) as exc:
        print("Timeout/connection error...waiting ~15 minutes to continue")
        time.sleep(1001)
        search_tweets(official_handle)

    # Stop temporarily when getting other errors
    except tweepy.TweepError as e:
        if 'Failed to send request:' in e.reason:
            print("Time out error caught.")
            time.sleep(1001)
            search_tweets(official_handle)
        elif 'Too Many Requests' in e.reason:
            print("Too many requests, sleeping for 15 min")
            time.sleep(1001)
            search_tweets(official_handle)
        else:
            print(e)
            print("Other error with this user...passing")
            pass

    return tweets


# Fetch last 20 tweets from
def user_tweets(official_handle):
    tweet = api.user_timeline(official_handle)
    return_list = []

    for i in range(0, len(tweet)):
        return_list.append({
            "Name": tweet[i]._json['user']['name'],
            "Handle": tweet[i]._json['user']['screen_name'],
            "Text": tweet[i]._json['text'],
            "Favorites": tweet[i]._json['favorite_count'],
            "Retweets": tweet[i]._json['retweet_count']
        })

    return return_list


# Get list of news articles about a politician
def get_news(official_name):
    # Create list for news sources
    newsLines = []

    # NewsAPI API call
    url = ('https://newsapi.org/v2/everything?'
           'apiKey=' + getNewsKey() + '&'
                                      'qInTitle=\"' + official_name + '\"&'
                                                                      'language=en&'
                                                                      'sortBy=publishedAt&'
                                                                      'pageSize=10')

    response = requests.get(url).json()['articles']

    # Format response by replacing any carriage returns and removing the brackets + ... at eol
    for line in response:
        if line['content'] is not None:
            article = line['content'].replace("\r\n", '')
            index = article.find('[')
            if index != -1:
                article = article[0:index - 3]
            newsLines.append({"Title": line['title'],
                              "Content": article,
                              "Source": line['source']['name'],
                              "URL": line['url']})

    return newsLines


# Get a 7 day timeline of news
def get_news_timeline(official_name):
    timeline = []
    for i in range(0, 7):

        # Create list for news sources
        newsLines = []

        # NewsAPI API call
        url = ('https://newsapi.org/v2/everything?'
               'apiKey=' + getNewsKey() + '&'
               'qInTitle=\"' + official_name + '\"&'
                                               'language=en&'
                                               'from=' + (
                       datetime.date.today() - datetime.timedelta(days=i)).isoformat() + '&' +
               'to=' + (datetime.date.today() - datetime.timedelta(days=i)).isoformat() + '&' +
               'sortBy=publishedAt&'
               'pageSize=5')

        response = requests.get(url).json()['articles']

        # Format response by replacing any carriage returns and removing the brackets + ... at eol
        for line in response:
            if line['content'] is not None:
                article = line['content'].replace("\r\n", '')
                index = article.find('[')
                if index != -1:
                    article = article[0:index - 3]
                newsLines.append(article)

        timeline.append(newsLines)

    return timeline

# print(search_tweets_timeline("JoeBiden"))
# print(user_tweets("JoeBiden"))
# getStateOfficials("az")
# work("SenMcSallyAZ")
# print(get_news_timeline("Joe Biden"))
# print(get_official_info("Donald Trump"))
