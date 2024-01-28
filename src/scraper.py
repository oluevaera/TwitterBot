from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re
import twitter_helper as th


class JobScraper:
    def __init__(self, url, title_css, id_css, date_css=None):
        self.url = url
        self.title_css = title_css
        self.id_css = id_css
        self.date_css = date_css
        self.open_positions = []

    def _get_job_details(self, company):
        driver = WebDriver().instance
        driver.get(self.url)
        driver.implicitly_wait(10)

        card_titles = driver.find_elements(By.CSS_SELECTOR, self.title_css)
        if company == "Google":
            card_urls = [
                element.get_attribute("href")
                for element in driver.find_elements(By.CSS_SELECTOR, self.id_css)
            ]
            card_ids = [card.split("results/")[1].split("-")[0] for card in card_urls]
        elif company == "Nvidia":
            card_urls = [element.get_attribute("href") for element in card_titles]
            card_ids = [
                element.text
                for element in driver.find_elements(By.CSS_SELECTOR, self.id_css)
            ]

        if self.date_css:
            card_dates = driver.find_elements(By.CSS_SELECTOR, self.date_css)[1::2]

        for i, (title, url, id) in enumerate(zip(card_titles, card_urls, card_ids)):
            job_title = title.text
            job_url = url
            job_id = id
            if self.date_css:
                job_date = re.sub(r"\W+", "", card_dates[i].text.split()[1])
                self.open_positions.append(
                    {
                        "title": job_title,
                        "url": job_url,
                        "id": job_id,
                        "date": job_date,
                    }
                )
            else:
                self.open_positions.append(
                    {"title": job_title, "url": job_url, "id": job_id}
                )

    def _filter_positions(self, company, posted_ids):
        # Filter by date, only applicable to Nvidia currently.
        if company == "Nvidia":
            self.open_positions = [
                pos
                for pos in self.open_positions
                if pos["date"] in ["Today", "Yesterday"]
            ]

        # Filter by id.
        self.open_positions = [
            pos for pos in self.open_positions if pos["id"] not in posted_ids
        ]

    def positions_to_post(self, company):
        self._get_job_details(company)
        posted_positions = th.read_latest_tweet_date(company)
        self._filter_positions(company, posted_positions)
        print(self.open_positions)
        return self.open_positions


class WebDriver:
    _instance = None

    def __init__(self):
        if not WebDriver._instance:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            WebDriver._instance = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )

    @property
    def instance(self):
        return WebDriver._instance

    def quit(self):
        if WebDriver._instance:
            WebDriver._instance.quit()
            WebDriver._instance = None


def main():
    google_scraper = JobScraper(
        url='https://careers.google.com/jobs/results/?location=Switzerland&q="software%20engineer"&sort_by=date',
        title_css="h3.QJPWVe",
        id_css="a.WpHeLc.VfPpkd-mRLv6.VfPpkd-RLmnJb",
    )

    nvidia_scraper = JobScraper(
        url="https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?jobFamilyGroup=0c40f6bd1d8f10ae43ffaefd46dc7e78&locationHierarchy1=2fcb99c455831013ea52e9ef1a0032ba",
        title_css="a.css-19uc56f",
        id_css="li.css-h2nt8k",
        date_css="dd.css-129m7dg",
    )

    companies = {"google": google_scraper, "nvidia": nvidia_scraper}

    for company in companies.keys():
        to_post = companies[company].positions_to_post(company.capitalize())

        for position in reversed(to_post):
            tweet = th.tweet_text(
                title=position["title"],
                url=position["url"],
                company=company.capitalize(),
                hashtag="#" + position["id"],
            )
            th.create_tweet(tweet)

        th.write_latest_tweet_date(company.capitalize(), to_post)


if __name__ == "__main__":
    main()
