import sys
import nltk
nltk.download('punkt')
from twitter import OAuth, Twitter

from requests_html import HTMLSession
import datetime
import pyshorteners

import credentials

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

oauth = OAuth(
        credentials.ACCESS_TOKEN,
        credentials.ACCESS_SECRET,
        credentials.CONSUMER_KEY,
        credentials.CONSUMER_SECRET
    )
t = Twitter(auth=oauth)


#Collect data from cards sidte and determine how many tweets to post.
def get_job_cards():
    session = HTMLSession()
    url = 'https://careers.google.com/jobs/results/?location=Switzerland&q=software%20engineer&sort_by=date'
    r = session.get(url)
    r.html.render(sleep=1, keep_page=True, scrolldown=1)

    cards = r.html.xpath('//a[@class="gc-card"]')
    card_dates = r.html.xpath('//div[@class="gc-card__header"]/meta[2]')
    dates = []
    for value in range(20):
        dates.insert(0, str(card_dates[value].attrs["content"]))

    latest_tweet_date = latest_tweet_dates_txt()
    tweet_T = datetime.datetime.strptime(latest_tweet_date[:-5], "%Y-%m-%dT%H:%M:%S")    
    for count in range (20):
        web_T = datetime.datetime.strptime(dates[count][:-5], "%Y-%m-%dT%H:%M:%S")
        if web_T > tweet_T:
            write_tweet_dates_txt(dates[-1])
            return cards[:20-count]


#Get the lastest tweet date.
def latest_tweet_dates_txt():
    with open('dates.txt') as f:
        latest = f.readlines()[-1]
        return latest


#Write the date of the latest collected card to dates.txt.
def write_tweet_dates_txt(new_tweet_date):
    with open('dates.txt', 'a') as f:
        f.write('\n')
        f.write(new_tweet_date)


#Keep dates.txt short.
def clean_tweet_dates_txt():
    with open('dates.txt', 'r+') as f:
        data = f.read().splitlines(True)
        if len(data) > 15:
            f.truncate(0)
            f.seek(0)
            f.writelines(data[10:])


#Collect the data from each Job card.
def handle_card_data(cards):
    if cards is None:
        sys.exit()

    clean_tweet_dates_txt()
    for item in reversed(cards):
        #Setup url/card and render JS.
        url = "https://careers.google.com" + item.attrs['href']
        session = HTMLSession()
        page = session.get(url)
        page.html.render(sleep=1, keep_page=True, scrolldown=1)
        
        #Collect the data of the job posting.
        title = item.attrs['aria-label']

        rendered_page_loc = page.html.xpath('//div[@class="wrapper__maincol"]//div[@itemprop="address"]/span')
        city = rendered_page_loc[0].text
        country = rendered_page_loc[1].text

        #Could be used in the future. Positions total count.
        job_matches = page.html.xpath('//div[@data-gtm-ref="jobs-matched"]/span/*')

        #Validate if position is available for remote working.
        remote_data = page.html.xpath('//li[@itemprop="jobLocationType"]')
        if remote_data:
            remote = remote_data[0].text
        else:
            remote = "Not eligible for remote working"

        tweet = create_text_paragraph(title, url, city, country, remote)
        t.statuses.update(status=tweet)
        print(tweet, end='\n')

#Functions that uses all the data collected for the job posting and creates the final message.
def create_text_paragraph(job_title, url, city, country, remote):
    #fStrings don't support '\' character.
    nl = '\n'
    nl_x2 = '\n'*2

    #Shorter URL since tweeter has a character limit(280).
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(url)

    #Unicode for bullet points. Could be used in the future.
    #bullet = '\n' + u'\u2022'

    msg = f"New position for:{nl}{job_title}{nl_x2}Main office: {city}, {country}{nl_x2}{remote}{nl_x2}Read more: {short_url}"

    return msg


x = get_job_cards()
handle_card_data(x)
