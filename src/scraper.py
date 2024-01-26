from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re
import twitter_helper as th


class JobScraper:
    def __init__(self, url, title_class, id_class, date_class=None):
        self.url = url
        self.title_class = title_class
        self.id_class = id_class
        self.date_class = date_class
        self.open_positions = []

    def _get_job_details(self):
        driver = WebDriver().instance
        driver.get(self.url)
        driver.implicitly_wait(10)

        card_titles = driver.find_elements(By.CLASS_NAME, self.title_class)
        card_ids = driver.find_elements(By.CLASS_NAME, self.id_class)

        if self.date_class:
            card_dates = driver.find_elements(By.CLASS_NAME, self.date_class)

        for title, ids in zip(card_titles, card_ids):
            job_title = title.text
            job_link = title.get_attribute("href")
            job_id = ids.text
            if self.date_class:
                job_date = re.sub(r"\W+", "", card_dates.text.split()[1])
                self.open_positions.append([job_title, job_link, job_id, job_date])
            else:
                self.open_positions.append([job_title, job_link, job_id])

    def _filter_positions(self, company, posted_id):
        # Filter by date, only applicable to Nvidia currently.
        if company == "Nvidia":
            self.open_positions = [
                pos for pos in self.open_positions if pos[-1] in ["Today", "Yesterday"]
            ]

        # Filter by id.
        self.open_positions = [
            pos for pos in self.open_positions if pos[2] not in posted_id
        ]

    def postitions_to_post(self, company):
        self._get_job_details()
        posted_positions = th.read_latest_teweet_date(company)
        to_post = self._filter_positions(company, posted_positions)
        return to_post


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
        title_class="QJPWVe",
        id_class=".WpHeLc.VfPpkd-mRLv6.VfPpkd-RLmnJb",
    )
    google_to_post = google_scraper.postitions_to_post("Google")

    nvidia_scraper = JobScraper(
        url="https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?jobFamilyGroup=0c40f6bd1d8f10ae43ffaefd46dc7e78&locationHierarchy1=2fcb99c455831013ea52e9ef1a0032ba",
        title_class="css-19uc56f",
        id_class="css-h2nt8k",
        date_class="css-129m7dg",
    )
    nvidia_to_post = nvidia_scraper.positions_to_post("Nvidia")
