from django.shortcuts import render
from django.http import HttpResponse
from .forms import StateForm, PersonForm
from django.template import Context
from PolitiStats.api import getStateOfficials, get_official_info, user_tweets
from PolitiStats.sentiment import gather_sentiment_news, gather_sentiment_mentions, gather_sentiment_tweets, \
    gather_news_timeline, gather_mentions_timeline


# form processing learned from youtube tutorial and https://stackoverflow.com/questions/10607091/how-can-i-access-the-form-submit-button-value-in-django
def home(request):
    # if request.method == "POST":
    if 'stateSearch' in request.POST:
        form = StateForm(request.POST)
        if form.is_valid():
            # state = form.cleaned_data['state']
            # print(state)
            state = request.POST['state']
            print("\n\n\n\n\n\n\n\n\ndropdown says:\n" + request.POST['state'] + "\n\n\n\n\n\n\n")
            officials = getStateOfficials(state.lower())
            apiOutput = {}

            # Since the API returs the office "us senator" once, we artificially add "us senator" at the beginning of the "offices" list. This is a good enough solution for now

            for idx, i in enumerate(officials):
                if idx == 0:
                    office = i.get('office').strip()
                    party = i.get('party').strip()
                    name = i.get('name').strip()

                    if office == "U.S. Senator":
                        office = "Senators"

                    if "Lieutenant Governor" in office:
                        office = "Lieutenant Governor"

                    elif "Governor" in office:
                        office = "Governor"

                    if state in office:
                        office = office.replace(state, "")

                    if office not in apiOutput:

                        apiOutput[office] = []
                        apiOutput[office].append(list([party, name]))
                    else:
                        apiOutput[office].append(list([party, name]))
                else:
                    office = officials[idx - 1].get('office').strip()
                    party = i.get('party').strip()
                    name = i.get('name').strip()

                    if office == "U.S. Senator":
                        office = "Senators"

                    if "Lieutenant Governor" in office:
                        office = "Lieutenant Governor"

                    elif "Governor" in office:
                        office = "Governor"

                    if state in office:
                        office = office.replace(state, "")

                    if office not in apiOutput:

                        apiOutput[office] = []
                        apiOutput[office].append(list([party, name]))
                    else:
                        apiOutput[office].append(list([party, name]))

            print(apiOutput)
            return render(request, 'results.html',
                          {'form': PersonForm(request.POST), "state_selected": state, "api_output": apiOutput})

    else:
        if request.method == "POST":
            # print("results click")
            # print(len(str(request.POST).splitlines()))
            textParse = ""
            for item in request.POST:
                textParse = textParse + item + "" + request.POST[item] + "\n"
            person = textParse.splitlines()[len(textParse.splitlines()) - 1]

            # the API returns name with middle initial. We might want to delete the middle initial when calling get_news()
            personNoMiddleInitial = person.split()[0] + " " + person.split()[len(person.split()) - 1]
            # print(person)
            state = request.POST['state']
            # print(getStateOfficials(state.lower()))

            FullApiDictionary = getStateOfficials(state.lower())
            personTwitterHandle = ""
            personFacebookHandle = ""
            personYouTubeHandle = ""

            for entry in FullApiDictionary:
                if entry['name'] == person and entry['socials'] != 'null':
                    # print(entry['socials'])
                    for socialAccount in entry['socials']:
                        if socialAccount['type'] == "Twitter":
                            # print(socialAccount['id'])
                            personTwitterHandle = socialAccount['id']
                        if socialAccount['type'] == "Facebook":
                            # print(socialAccount['id'])
                            personFacebookHandle = socialAccount['id']
                        if socialAccount['type'] == "YouTube":
                            # print(socialAccount['id'])
                            personYouTubeHandle = socialAccount['id']

            print(get_official_info(person)['Image'])
            # print('\n\n\n\n\n\n'+personTwitterHandle+'\n\n\n')

            bio_index = get_official_info(person)['Description'][0:300].rfind('.')
            sentiment_news, news_articles = gather_sentiment_news(personNoMiddleInitial)

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
                           "news_timeline": gather_news_timeline(personNoMiddleInitial),
                           "mentions_timeline": gather_mentions_timeline(personTwitterHandle)})

            # return render(request, 'analysis.html', {"person_selected": person, "person_image": get_official_info(person)['Image'], "person_details_1": get_official_info(person)['Description'][0:bio_index+1], "person_details_2": get_official_info(person)['Description'][bio_index+1:-1], "sentiment_news": "test", "sentiment_tweets": "test", "sentiment_mentions": "test", "twitter_link": "https://twitter.com/" + personTwitterHandle, "facebook_link": "https://facebook.com/" + personFacebookHandle, "youtube_link": "https://youtube.com/" + personYouTubeHandle})

    form = StateForm()
    return render(request, 'home.html', {'form': form})

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
