import sys
from requests_html import HTMLSession
from datetime import datetime
import twitter_helper as th
import pyshorteners


# Get list of job cards and determine how many tweets to post.
def get_google_job_cards():
    session = HTMLSession()
    url = ('https://careers.google.com/jobs/results/?location=Switzerland'
           '&q=software%20engineer&sort_by=date'
           )
    page = session.get(url)
    page.html.render(sleep=1, keep_page=True, scrolldown=1)
    
    # Get the dates of all first page postings.
    cards = page.html.xpath('//a[@class="gc-card"]')
    card_dates = page.html.xpath('//div[@class="gc-card__header"]/meta[2]')
    dates = list()
    
    # Posting dates are sorted by date, so:
    # 'insert' instead of 'append' to store them from oldest[0] -> newest[19].
    for value in range(len(card_dates)):
        dates.insert(0, str(card_dates[value].attrs["content"]))


    # Figure how many posts to create based on the last posted tweet date.
    tweet_t_pre_edit = th.read_latest_tweet_date('Google')
    tweet_t = datetime.strptime(tweet_t_pre_edit[:-5], "%Y-%m-%dT%H:%M:%S")

    cards_length = len(cards)  
    for count in range(cards_length):
        web_t = datetime.strptime(dates[count][:-5], "%Y-%m-%dT%H:%M:%S")
        if web_t > tweet_t:
            th.write_latest_tweet_date('Google', dates[-1])
            return cards[:cards_length-count]


# Collect the data from each Job card.
def handle_card_data(card):
    session = HTMLSession() 
    url = "https://careers.google.com" + card.attrs['href']
    page = session.get(url)
    page.html.render(sleep=1, keep_page=True, scrolldown=1)
    
    # Collect the data from job posting.
    title = card.attrs['aria-label']
    try:
        rendered_page_loc = page.html.xpath(
            '//div[@class="wrapper__maincol"]//div[@itemprop="address"]/span'
            )
        city = rendered_page_loc[0].text[:-1]
        country = rendered_page_loc[1].text

    except Exception: 
        city = "Not specified"
        country = " -"

    # Check if position is available for remote working.
    remote_data = page.html.xpath('//li[@itemprop="jobLocationType"]')
    if remote_data:
        remote = remote_data[0].text
    else:
        remote = "Not eligible for remote working"
        
    type_tiny = pyshorteners.Shortener()
    tiny_url = type_tiny.tinyurl.short(url)
    tweet = th.tweet_text(title, tiny_url, city, country, remote, 'Google')
    th.create_tweet(tweet)


# Control the script and exit if there are no new job postings.
def main():
    cards = get_google_job_cards()
    if cards is None:
        sys.exit()

    for card in reversed(cards):
        handle_card_data(card)


if __name__ == "__main__":
    main()
