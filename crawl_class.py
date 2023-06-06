from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from bs4 import BeautifulSoup as bs
import json
import requests
from abc import ABC, abstractmethod
import time

DEBUG = False


class Crawler(ABC):
    @abstractmethod
    def get_website(self, url):
        return NotImplementedError

    @abstractmethod
    def additional_action(self, url):
        return NotImplementedError

    @abstractmethod
    def get_data(self, url):
        return NotImplementedError


class GainTradeSelenium(webdriver.Chrome, Crawler):
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

    def __init__(
        self,
        options: list = [],
    ):
        option = Options()
        option.add_argument("--start-maximized")
        if options:
            option.add_experimental_option("detach", True)
            for opt in options:
                option.add_argument(opt)
        super(GainTradeSelenium, self).__init__(options=option)

    def additional_action(self, by, path):
        """
        action must be tuple that include (By, path)
        """
        if by and path:
            try:
                elem = self.find_element(self.by_dict[by], path)
                elem.click()
            except NoSuchElementException:
                if DEBUG:
                    print("No such element in this path")

    def change_network(self, by, paths, **kwargs):
        for path in paths:
            self.additional_action(by, path)

    def close(self):
        return super().close()

    def get_data(self, by, path, waiting_loader="..."):
        by = self.by_dict[by.lower()]
        item = waiting_loader
        trying = 0
        while waiting_loader in item:
            item = WebDriverWait(self, 5).until(
                EC.presence_of_element_located((by, path))
            )
            item = item.text
            if trying == 3 or waiting_loader not in item:
                break
            else:
                time.sleep(2)
                trying += 1
            print(item)
        return item

    def get_website(self, url):
        self.get(url)


class BsCrawl(Crawler):
    """
    An Abstract Method for Eur Usd Crawl, it makes easy to build New Website if You want
    """

    def __init__(self, url: str, method: str = "get", payload: dict = {}) -> None:
        self.url = url
        self.method = method
        self.payload = payload
        self.response = requests.request(
            method=method.upper(), url=url, headers=self.headers, data=payload
        )
        self.__build_item()
        self.by_dict = {
            "css": lambda content, path: self.__css(content, path),
            "xpath": lambda content, path: self.__xpath(content, path),
        }

    def get_website(self, url):
        self.response(url=url)

    def parsing(self, by, path, get_first=False):
        soup = bs(self.response.text, "html.parser")
        item = self.by_dict[by](str(soup), path)
        if get_first:
            item = item[0]
        item = self.pre_process(item)
        return item

    def add_other_item(self, items: dict):
        for item_name, item in items.items():
            self.data_crawl[item_name] = item

    def __css(self, content, path):
        item = etree.fromstring(content)
        item = item.cssselect(path)
        return item

    def __xpath(self, content, path):
        item = etree.HTML(content)
        item = item.xpath(path)
        return item


class CrawlSerializer:
    def get_serializer(self, crawler_use: str, **kwargs):
        if crawler_use.lower() == "selenium":
            return GainTradeSelenium(kwargs.get("options", []))
        elif crawler_use.lower() == "bs":
            return BsCrawl(**kwargs)
