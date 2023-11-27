from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import os


class Downloader:
    download_dir = os.getcwd() + "\\input"

    def __init__(self, data_dir: str) -> None:
        self.option = webdriver.ChromeOptions()
        self.option.add_argument("--user-data-dir=" + data_dir)
        # self.option.add_argument("headless")
        prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": self.download_dir,
        }
        self.option.add_experimental_option("prefs", prefs)
        self.driver: webdriver.Chrome = webdriver.Chrome(
            chrome_options=self.option, executable_path="chromedriver.exe"
        )
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def openWebsite(self, website: str):
        self.driver.get(website)

    def downloadFromText(self, text: str):
        outerElement = self.driver.find_element(
            By.CSS_SELECTOR,
            "#root > div > div > div:nth-child(2) > div:nth-child(3) > div.clickable > span > span:nth-child(1)",
        )
        if outerElement.text == "+":
            outerElement.click()
        for css in [
            "#root > div > div > div:nth-child(2) > div:nth-child(3) > div:nth-child(2) > div > div > div:nth-child(4) > div.clickable > span > span:nth-child(1)",
            "#root > div > div > div:nth-child(2) > div:nth-child(3) > div:nth-child(2) > div > div > div:nth-child(3) > div.clickable > span > span",
            "#root > div > div > div:nth-child(2) > div:nth-child(3) > div:nth-child(2) > div > div > div:nth-child(5) > div.clickable > span > span",
        ]:
            element = self.driver.find_element(By.CSS_SELECTOR, css)
            if element.text == "-":
                element.click()
        self.driver.find_element(By.XPATH, '//a[text()="{0}"]'.format(text)).click()
        sleep(1)

    def quit(self):
        self.driver.quit()
