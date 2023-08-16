import sys
from requests_html import HTMLSession
import twitter_helper as th


# Get list of job cards and determine how many tweets to post.
def get_google_job_cards():
    session = HTMLSession()
    url = ('https://careers.google.com/jobs/results/?location=Switzerland'
           '&q=software%20engineer&sort_by=date'
           )
    page = session.get(url)
    page.html.render(sleep=1, keep_page=True, scrolldown=1)
    
    # Get the dates of all first page postings.
    cards = page.html.xpath('//li[@class="lLd3Je"]/div')
    active_jobs_tags = list()
    for card in cards:
        active_jobs_tags.append(card.attrs["jsdata"].split(';')[1])
    
    posted_job_tags = th.read_latest_tweet_date('Google')

    to_be_posted = list()
    for i, job in enumerate(active_jobs_tags, 1):
        if job in posted_job_tags:
            continue
        
        title = page.html.xpath(f'//li[@class="lLd3Je"][{i}]/div//h3')[0].text
        job_link = 'https://www.google.com/about/careers/applications/jobs/results/' + job
        job_id = job
        experience = page.html.xpath(f'//li[@class="lLd3Je"][{i}]//span[@class="wVSTAb"]')[0].text + ' level'
        to_be_posted.append([title, job_link, job_id, experience])

    return to_be_posted


# Control the script and exit if there are no new job postings.
def main():
    to_post = get_google_job_cards()
    if to_post is None:
        sys.exit()

    city = 'Zürich'
    country = 'Switzerland'
    for position in reversed(to_post):
        tweet = th.tweet_text(position[0], position[1], city, country,
                              'Google', '#' + position[2], position[3]
                              )
        th.create_tweet(tweet)
    th.write_latest_tweet_date('Google', to_post)


if __name__ == "__main__":
    main()
