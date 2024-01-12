import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import twitter_helper as th


# Collect the data from the nvidia careers website.
def get_nvidia_job_details():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    url = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?jobFamilyGroup=0c40f6bd1d8f10ae43ffaefd46dc7e78&locationHierarchy1=2fcb99c455831013ea52e9ef1a0032ba"
    driver.get(url)
    driver.implicitly_wait(10)

    # Get the data of all the jobs (up to 20) from the careers website.
    card_titles = driver.find_elements(By.CLASS_NAME, "css-19uc56f")
    card_ids = driver.find_elements(By.CLASS_NAME, "css-h2nt8k")
    card_dates = driver.find_elements(By.CLASS_NAME, "css-129m7dg")
    open_positions = list()

    # Populate a list with all the collected job data.
    for title, ids, dates in zip(card_titles, card_ids, card_dates[1::2]):
        job_title = title.text
        job_link = title.get_attribute("href")
        job_id = ids.text
        job_date = re.sub(r"\W+", "", dates.text.split()[1])  # remove the '+'.
        open_positions.append([job_title, job_link, job_id, job_date])

    driver.quit()
    return open_positions


# Filter the open positions based on the post date.
def filtered_positions(open_positions, todays_tags):
    filter_by_time = [
        position
        for position in open_positions
        if position[-1] == "Today" or position[-1] == "Yesterday"
    ]

    # Filter the open positions based on the tag.
    filter_by_tag = [
        position for position in filter_by_time if position[2] not in todays_tags
    ]

    return filter_by_tag


def main():
    open_positions = get_nvidia_job_details()
    todays_tags = th.read_latest_tweet_date("Nvidia")

    to_post = filtered_positions(open_positions, todays_tags)
    if not to_post:
        sys.exit()

    city = "Zürich"
    country = "Switzerland"

    for position in reversed(to_post):
        tweet = th.tweet_text(
            position[0], position[1], city, country, "Nvidia", "#" + position[-2]
        )
        th.create_tweet(tweet)

    th.write_latest_tweet_date("Nvidia", to_post)


if __name__ == "__main__":
    main()
