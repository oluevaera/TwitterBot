import tweepy
import os
from datetime import date, timedelta
import json


client = tweepy.Client(
    consumer_key=os.environ['CONSUMER_KEY'],
    consumer_secret=os.environ['CONSUMER_SECRET'],
    access_token=os.environ['ACCESS_TOKEN'],
    access_token_secret=os.environ['ACCESS_SECRET']
)


def read_latest_tweet_date(company):
    with open('data.json') as file:
        json_data = json.load(file)

    if company == 'Google':
        google_latest = json_data[company]['date']
        return google_latest
    elif company == 'Nvidia':
        date_today = date.today()
        date_yesterday = date_today - timedelta(days=1)
        nvidia_latest = [
            dic['id'] for dic in json_data[company] if
            dic['day'] == str(date_today) or dic['day'] == str(date_yesterday)
            ]
        return nvidia_latest


def write_latest_tweet_date(company, data):
    with open('data.json') as file:
        existing_data = json.load(file)

    if company == 'Google':
        existing_data[company]['date'] = data
    elif company == 'Nvidia':
        for posting in data:
            existing_data[company].append(
                {"day": str(date.today()), "id": posting[-2]}
                )
        while len(existing_data[company]) > 20:
            existing_data[company].pop(0)

    with open('data.json', 'w') as file:
        json.dump(existing_data, file)


# Function that uses all the data collected from the job postings and returns
# the final tweet text.
def tweet_text(job_title, url, city, country, remote, company, hashtag=''):

    msg = (
    f'New position for:\n'
    f'{job_title}\n'
    f'\n'
    f'Main office: {city}, {country}\n'
    f'\n'
    f'{remote}\n'
    f'\n'
    f'Read more: {url}\n'
    f'#{company} {hashtag}'
    )

    return msg


def create_tweet(tweet):
    client.create_tweet(text=tweet)
