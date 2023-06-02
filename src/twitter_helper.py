import tweepy
import os

# Authenticate tweepy to post and retrieve data.
# Currently using API v1.1
auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_SECRET'])
api = tweepy.API(auth) 


def get_company_hashtag_details(company):
    # This list is currently populated by Nvidia tweets only.
    dates_and_tags = list()

    # Iterate over the latest 100 tweets of the user.
    for tweet in tweepy.Cursor(
        api.user_timeline,
        screen_name='@GoogleJobAds',
        tweet_mode='extended'
        ).items(100):
        
        # Get all the hashtags of the tweet
        post_hashtags = tweet._json['entities']['hashtags']
        
        # If we reach the old no-hashtag format
        # This should be deleated after 100  # posts.
        if post_hashtags == [] and company == 'Nvidia':
           return dates_and_tags 

        # If the tweet has the Nvidia hashtag, then populate a list with all the
        # second hashtag values. (Second hash is an ID)
        if company == 'Nvidia' and company in post_hashtags[0].values():
            date_time = str(tweet.created_at.replace(tzinfo=None)).split(' ')
            second_hashtag = post_hashtags[1]['text']
            date_time.append(second_hashtag)
            dates_and_tags.append(date_time)

        # If the tweet has the Google hashtag, then return the latest date.
        elif company == 'Google' and company in post_hashtags[0].values():
            date_time = str(tweet.created_at.replace(tzinfo=None)).split(' ')
            return date_time

    return dates_and_tags
            
            
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
    api.update_status(tweet)
