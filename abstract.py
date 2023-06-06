from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import namedtuple
import time
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s  %(filename)s:%(lineno)d: %(message)s",
    datefmt="[%d-%m-%Y] %H:%M:%S",
)


class SeleniumCrawl(webdriver.Chrome):
    by_dict = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
        "tag_name": By.TAG_NAME,
        "class_name": By.CLASS_NAME,
        "css_selector": By.CSS_SELECTOR,
    }

    def __init__(self, *args, **kwargs):
        options = Options()
        options.add_argument("--start-maximized")
        if kwargs.get("debug", False):
            kwargs.pop("debug")
            options.add_experimental_option("detach", True)
        if args:
            for opt in args:
                options.add_argument(opt)
        super(SeleniumCrawl, self).__init__(options=options, *args, **kwargs)

    def get_website(self, url):
        self.get(url)
        self.implicitly_wait(5)

    def get_element(self, by, path, need_wait=False):
        try:
            if need_wait:
                elem = WebDriverWait(self, 30).until(
                    EC.presence_of_element_located((self.by_dict[by], path))
                )
                self.implicitly_wait(2)
            else:
                elem = self.find_element(by=self.by_dict[by], value=path)
            return elem
        except NoSuchElementException:
            logging.warning("No Element in that path, Try changing path or by")
        except TimeoutException:
            raise TimeoutException("Please Check your connection")

    def change_pair_or_network(self, by, *args, **kwargs):
        for path in args:
            fmt_path = path.format(**kwargs)
            elem = self.get_element(by, fmt_path, kwargs.get("need_wait", False))
            time.sleep(2)
            elem.click()

    def find_data(self, **kwargs):
        data = {}
        self.implicitly_wait(5)
        for key, value in kwargs.items():
            if value.get("path"):
                elem = self.get_element(value.get("by"), value.get("path"))
                data[key] = elem.text
            else:
                data[key] = None
        return data

    def cloes(self):
        super().close()
