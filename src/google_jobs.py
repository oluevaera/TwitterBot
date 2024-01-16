import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import twitter_helper as th


# Get list of job cards and determine how many tweets to post.
def get_google_job_cards():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    url = 'https://careers.google.com/jobs/results/?location=Switzerland&q="software%20engineer"&sort_by=date'
    driver.get(url)
    driver.implicitly_wait(10)

    # Get the data of all the jobs from the careers website.
    card_titles = driver.find_elements(By.CLASS_NAME, "QJPWVe")
    card_url = [
        element.get_attribute("href")
        for element in driver.find_elements(
            By.CSS_SELECTOR, ".WpHeLc.VfPpkd-mRLv6.VfPpkd-RLmnJb"
        )
    ]
    card_ids = [card.split("results/")[1].split("-")[0] for card in card_url]
    open_positions = list()

    # Populate a list with all the collected job data.
    for title, id, url in zip(card_titles, card_ids, card_url):
        job_title = title.text
        job_link = url
        job_id = id
        open_positions.append([job_title, job_link, job_id, ""])

    driver.quit()
    return open_positions


# Filter the open positions based on the tag.
def filtered_positions(open_positions, posted_positions):
    filter_by_tag = [
        position for position in open_positions if position[2] not in posted_positions
    ]

    return filter_by_tag


# Control the script and exit if there are no new job postings.
def main():
    open_positions = get_google_job_cards()
    posted_positions = th.read_latest_tweet_date("Google")

    to_post = filtered_positions(open_positions, posted_positions)
    if not to_post:
        sys.exit()

    city = "Zürich"
    country = "Switzerland"
    for position in reversed(to_post):
        tweet = th.tweet_text(
            position[0], position[1], city, country, "Google", "#" + position[2]
        )
        th.create_tweet(tweet)
    th.write_latest_tweet_date("Google", to_post)


if __name__ == "__main__":
    main()
