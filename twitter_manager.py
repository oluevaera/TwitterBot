import os
import tweepy
from datetime import date
import pyshorteners

auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_SECRET'])
api = tweepy.API(auth) 

def get_company_hashtag_details(company):
    # Access the user tweets.
    for tweet in tweepy.Cursor(
        api.user_timeline,
        screen_name='@GoogleJobAds',
        tweet_mode='extended'
        ).items():
        
        # Get all the hashtags per tweet
        post_hashtags = tweet._json['entities']['hashtags']

        # If there are two hashtags return date of the post and the text of the
        # second hashtag.
        if  len(post_hashtags) == 2:
            if company in post_hashtags[0].values():
                date_time = str(tweet.created_at.replace(tzinfo=None)).split(' ')
                second_hashtag = post_hashtags[1]['text']
                date_time.append(second_hashtag)
                return date_time
            
        # Else return just the dates.
        elif len(post_hashtags) == 1:
            if company in post_hashtags[0].values():
                date_time = str(tweet.created_at.replace(tzinfo=None)).split(' ')
                return date_time
            
            
# Make a dictionary containing the date and time and and #ID if it exists for
# each company.
def tweet_details_collector(company):
    tweet_dates = dict()
    date_today = date.today()

    date_time = get_company_hashtag_details(company)
    tweet_dates[company] = date_time
    
    return tweet_dates
    

# Function that uses all the data collected from the job postings and returns
# the final message.
def tweet_text(job_title, url, city, country, remote, company, hashtag=''):
    # Shorter URL since twitter has a character limit(280).
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(url)

    msg = f"""
    New position for:
    {job_title}
    
    Main office: {city}, {country}
    
    {remote}
    
    Read more: {short_url}
    #{company} {hashtag}
    """
    return msg

    
def create_tweet(tweet):
    api.update_status(tweet)
