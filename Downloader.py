from selenium import webdriver
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
        try:
            self.driver.find_element_by_xpath(
                '//a[text()="[{0}]"]'.format(text)
            ).click()
        except Exception:
            self.driver.find_element_by_xpath('//span[text()="时间轴标记"]').click()
            self.driver.find_element_by_xpath(
                '//a[text()="[{0}]"]'.format(text)
            ).click()
        finally:
            sleep(1)

    def quit(self):
        self.driver.quit()
