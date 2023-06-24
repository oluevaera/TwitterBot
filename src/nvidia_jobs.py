import re
from requests_html import HTMLSession
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

    return open_positions


# Filter the open positions based on the post date.
def filtered_positions(open_positions, todays_tags):
    filter_by_time = [position for position in open_positions if
                      position[-1] == "Today" or position[-1] == '10']

    # Filter the open positions based on the tag.
    filter_by_tag = [position for position in filter_by_time if
                      position[2] not in todays_tags
                      ]

    return filter_by_tag


def main():
    open_positions = get_nvidia_job_details()
    todays_tags = th.read_latest_tweet_date('Nvidia')

    to_post = filtered_positions(open_positions, todays_tags)

    city = 'Zürich'
    country = 'Switzerland'
    remote = 'Not eligible for remote working.'

    for position in reversed(to_post):
        tweet = th.tweet_text(position[0], position[1], city, country,
                              remote, 'Nvidia', '#' + position[-2]
                              )
        th.create_tweet(tweet)

    th.write_latest_tweet_date('Nvidia', to_post)


if __name__ == "__main__":
    main()
