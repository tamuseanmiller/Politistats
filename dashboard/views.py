from django.shortcuts import render
from django.http import HttpResponse
from .forms import PersonForm
from django.template import Context
from PolitiStats.api import getStateOfficials, get_official_info, user_tweets
from PolitiStats.sentiment import gather_sentiment_news, gather_sentiment_tweets, gather_sentiment_mentions, gather_news_timeline, gather_mentions_timeline


def dashboard(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.cleaned_data['person']

            listOfStates = ["AL","AK","AZ","AR","CA","CO","CT","DE", "DC","FL","GA", "HI","ID","IL","IN","IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
            personTwitterHandle = ""
            personFacebookHandle = ""
            personYouTubeHandle = ""           
            for state in listOfStates:
                FullApiDictionary = getStateOfficials(state.lower())

                for entry in FullApiDictionary:
                    entryNameNoMI = entry['name'].split()[0] + " "  +  entry['name'].split()[len( entry['name'].split()) - 1]
                    
                    if entryNameNoMI.lower() == person.lower() and entry['socials'] != 'null':
                        #print(entry['socials'])
                        for socialAccount in entry['socials']:
                            if socialAccount['type'] == "Twitter":
                                #print(socialAccount['id'])
                                personTwitterHandle = socialAccount['id']
                            if socialAccount['type'] == "Facebook":
                                #print(socialAccount['id'])
                                personFacebookHandle = socialAccount['id']
                            if socialAccount['type'] == "YouTube":
                                #print(socialAccount['id'])
                                personYouTubeHandle = socialAccount['id']

            #We currently only have the name of the person. To get social handles, we need to get the state, and search the API output for the handle
            #return render(request, 'analysis.html', {"person_selected": person, "sentiment_news": gather_sentiment_news(person)})
            bio_index = get_official_info(person)['Description'][0:300].rfind('.')
            sentiment_news, news_articles = gather_sentiment_news(person)  
            #return render(request, 'analysis.html', {"person_selected": person, "sentiment_news": "n/a"})
            #return render(request, 'analysis.html', {"person_selected": person, "person_image": get_official_info(person)['Image'], "person_details_1": get_official_info(person)['Description'][0:bio_index+1], "person_details_2": get_official_info(person)['Description'][bio_index+1:-1], "sentiment_news": gather_sentiment_news(entryNameNoMI), "sentiment_tweets": gather_sentiment_tweets(personTwitterHandle), "sentiment_mentions": gather_sentiment_mentions(personTwitterHandle), "twitter_link": "https://twitter.com/" + personTwitterHandle, "facebook_link": "https://facebook.com/" + personFacebookHandle, "youtube_link": "https://youtube.com/" + personYouTubeHandle, "user_tweets": user_tweets(personTwitterHandle), "news_timeline": gather_news_timeline(entryNameNoMI), "mentions_timeline": gather_mentions_timeline(personTwitterHandle)})
            
            return render(request, 'analysis.html',
                          {"person_selected": person, "person_image": get_official_info(person)['Image'],
                           "person_details_1": get_official_info(person)['Description'][0:bio_index + 1],
                           "person_details_2": get_official_info(person)['Description'][bio_index + 1:-1],
                           "sentiment_news": sentiment_news,
                           "news_articles": news_articles,
                           "sentiment_tweets": gather_sentiment_tweets(personTwitterHandle),
                           "sentiment_mentions": gather_sentiment_mentions(personTwitterHandle),
                           "twitter_link": "https://twitter.com/" + personTwitterHandle,
                           "facebook_link": "https://facebook.com/" + personFacebookHandle,
                           "youtube_link": "https://youtube.com/" + personYouTubeHandle,
                           "user_tweets": user_tweets(personTwitterHandle),
                           "news_timeline": gather_news_timeline(person),
                           "mentions_timeline": gather_mentions_timeline(personTwitterHandle)})

    form = PersonForm()
    return render(request, 'dashboard.html', {'form': form})

# def home(request):
#     states = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "Delaware",
#               "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana",
#               "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana",
#               "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada",
#               "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
#               "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin",
#               "West Virginia", "Wyoming"]
#
#     context = {
#         'states': states
#     }
#     return render(request, 'home.html', context)
