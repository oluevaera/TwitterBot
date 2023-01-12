import re
from requests_html import HTMLSession
from datetime import date, datetime, timedelta
import pyshorteners
import twitter_helper as th


# Collect the data from the nvidia careers website.
def get_nvidia_job_details():
    # Render the careers page.
    session = HTMLSession()
    url = (
        'https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite'
        '?locations=91336993fab910af6d6f80c09504c167'
        '&jobFamilyGroup=0c40f6bd1d8f10ae43ffaefd46dc7e78'
        )
    page = session.get(url)
    page.html.render(sleep=5, keep_page=True, scrolldown=1)
    
    # The script runs multiple times each day.
    # Collect all the nvidia job IDs for jobs that are already tweeted today or
    # yesterday.
    date_today = date.today()
    date_yesterday = date_today - timedelta(days=1)
    todays_tags = [el[2] for el in th.get_company_hashtag_details('Nvidia') if
                   el[0] == str(date_today) or el[0] == str(date_yesterday)
                   ]

    # Find how long has it been between the latest nvidia job tweet and today.
    latest_nvidia_tweet = th.get_company_hashtag_details('Nvidia')
    latest_tweet_date = datetime.strptime(latest_nvidia_tweet[0][0], "%Y-%m-%d")
    current_date = datetime.strptime(str(date.today()), "%Y-%m-%d")
    time_diff = str(current_date - latest_tweet_date)
    
    # Get the data of all the jobs (up to 20) from the careers website. 
    card_titles = page.html.xpath('//a[@class="css-19uc56f"]') 
    card_ids = page.html.xpath('//li[@class="css-h2nt8k"]')
    card_dates = page.html.xpath('//dd[@class="css-129m7dg"]') 
    open_positions = list()
    type_tiny = pyshorteners.Shortener()

    # Populate a list with all the collected job data.
    for title, ids, dates in zip(card_titles, card_ids,card_dates[1::2]):
        job_title = title.text
        job_link = "https://nvidia.wd5.myworkdayjobs.com" + title.attrs["href"]
        job_id = ids.text
        job_date = re.sub(r'\W+', '', dates.text.split()[1]) # remove the '+'.
        short_url = type_tiny.tinyurl.short(job_link)
        open_positions.append([job_title, short_url, job_id, job_date])
   
    # Filter the open positions based on the post date.
    open_positions = [position for position in open_positions if
                      position[-1] == "Today" or
                      position[-1] <= time_diff
                      ]

    # Filter the open positions based on the tag.
    open_positions = [position for position in open_positions if
                      position[2] not in todays_tags
                      ]
    
    return open_positions
    
    
def main():
    open_positions = get_nvidia_job_details()
    city = 'Zürich'
    country = 'Switzerland'
    remote = 'Not eligible for remote working.'

    for position in reversed(open_positions):
        tweet = th.tweet_text(position[0], position[1], city, country,
                              remote, 'Nvidia', '#' + position[-2]
                              )
        th.create_tweet(tweet)


if __name__ == "__main__":
    main()