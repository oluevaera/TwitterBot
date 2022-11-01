import sys
import os

from twitter import OAuth, Twitter
import tweepy
from requests_html import HTMLSession
import datetime
import pyshorteners

#import credentials


#Setup for running over 'Github actions' or local Terminal with credentials.

#Local tessting:
#oauth = OAuth(
#        credentials.ACCESS_TOKEN,
#        credentials.ACCESS_SECRET,
#        credentials.CONSUMER_KEY,
#        credentials.CONSUMER_SECRET
#    )
#t = Twitter(auth=oauth)

#Github Actions run:
oauth = OAuth(
    os.environ['ACCESS_TOKEN'],
    os.environ['ACCESS_SECRET'],
    os.environ['CONSUMER_KEY'],
    os.environ['CONSUMER_SECRET']
)
t = Twitter(auth=oauth)


def get_latest_tweet_date():
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_SECRET'])
    api = tweepy.API(auth)
    tweets_list= api.user_timeline(count=1) # Get the last tweet.
    tweet = tweets_list[0] # An object of class Status (tweepy.models.Status).
    return tweet.created_at.replace(tzinfo=None) # Remove the timezone from the timestamp.


def load_page(url):
    session = HTMLSession()
    return  session.get(url)


# Get list of job cards and determine how many tweets to post.
def get_job_cards():
    url = 'https://careers.google.com/jobs/results/?location=Switzerland&q=software%20engineer&sort_by=date'
    page = load_page(url)
    page.html.render(sleep=1, keep_page=True, scrolldown=1)
    
    # get the dates of all 20 Job postings.
    cards = page.html.xpath('//a[@class="gc-card"]')
    card_dates = page.html.xpath('//div[@class="gc-card__header"]/meta[2]')
    dates = []
    
    # Posting dates are sorted by date, so:
    # 'insert' instead of 'append' to store them from oldest[0] -> newest[19].
    for value in range(len(card_dates)):
        dates.insert(0, str(card_dates[value].attrs["content"]))

    # Figure how many posts to create based on the last posted tweet date.
    tweet_t = get_latest_tweet_date()    
    for count in range (20):
        web_t = datetime.datetime.strptime(dates[count][:-5], "%Y-%m-%dT%H:%M:%S")
        if web_t > tweet_t:
            return cards[:20-count]


# Collect the data from each Job card.
def handle_card_data(card):
    url = "https://careers.google.com" + card.attrs['href']
    page = load_page(url)
    page.html.render(sleep=1, keep_page=True, scrolldown=1)
    
    #Collect the data from job posting.
    title = card.attrs['aria-label']
    try:
        rendered_page_loc = page.html.xpath('//div[@class="wrapper__maincol"]//div[@itemprop="address"]/span')
        city = rendered_page_loc[0].text
        country = rendered_page_loc[1].text
        #Could be used in the future. Positions total count.
        #job_matches = page.html.xpath('//div[@data-gtm-ref="jobs-matched"]/span/*')
    except Exception: 
        city = "Not specified"
        country = " -"

    #Check if position is available for remote working.
    remote_data = page.html.xpath('//li[@itemprop="jobLocationType"]')
    if remote_data:
        remote = remote_data[0].text
    else:
        remote = "Not eligible for remote working"
    tweet = create_text_paragraph(title, url, city, country, remote)
    t.statuses.update(status=tweet)


# Function that uses all the data collected from the job posting and returns the final message.
def create_text_paragraph(job_title, url, city, country, remote):
    # fStrings don't support '\' character.
    nl = '\n'
    nl_x2 = '\n'*2

    # Shorter URL since twitter has a character limit(280).
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(url)

    # Unicode for bullet points. Could be used in the future.
    # bullet = '\n' + u'\u2022'

    msg = f"New position for:{nl}{job_title}{nl_x2}Main office: {city}, {country}{nl_x2}{remote}{nl_x2}Read more: {short_url}"

    return msg


# Control the script and exit if there are no new job postings.
def main():
    cards = get_job_cards()
    if cards is None:
        sys.exit()

    for card in reversed(cards):
        handle_card_data(card)


if __name__ == "__main__":
    main()