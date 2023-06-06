from typing import Any
from bs4 import BeautifulSoup as bs
import requests
import json
from lxml import etree
from abc import ABC, abstractmethod
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_crawl import GainTradeSelenium


# Init Selenium
options = Options()
options.add_experimental_option("detach", True)
# options.add_argument("--headless")


class EurUsdCrawl(ABC):
    """
    An Abstract Method for Eur Usd Crawl, it makes easy to build New Website if You want
    """

    def __init__(self, url: str, method: str, payload: dict = {}) -> None:
        self.url = url
        self.method = method
        self.payload = payload
        self.response = requests.request(
            method=method.upper(), url=url, headers=self.headers, data=payload
        )

    @abstractmethod
    def parsing(
        self,
    ):
        raise NotImplementedError

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.data_crawl

    def add_other_item(self, items: dict):
        for item_name, item in items.items():
            self.data_crawl[item_name] = item


class Apollox(EurUsdCrawl):
    url = "https://www.apollox.finance/en/futures/v2/EURUSD"
    method = "get"
    xpath = "//head/title/text()"
    get_first = True
    payload = {}

    def __init__(self) -> None:
        super().__init__(self.url, self.method, self.payload)

    def parsing(self):
        soup = bs(self.response.text, "html.parser")
        doc = etree.HTML(str(soup))
        item = doc.xpath(self.xpath)
        if self.get_first:
            item = item[0]
        item = self.pre_process(item)
        self.data_crawl["price"] = item

    def pre_process(self, item: str):
        item = item.split("|")[0]
        return item


def creating_data_from_obj(file_name: str, data):
    data = {"data": data}
    with open(f"{file_name}.json", "w") as f:
        f.write(json.dumps(data))
    return data


def main(file_name, **kwargs):
    data = {}
    apollox = Apollox()
    apollox.parsing()
    apollox.add_other_item(
        {"network": "BNB Chain", "website": "apollox.finance", "pair": "EURUSD"}
    )
    data["apollox"] = apollox()

    # Gain Trade crawl start

    # Polygon
    polygon = GainTradeSelenium(options)
    data["polygon"] = polygon.run(
        "https://gains.trade/trading#EUR-USD",
        network=(By.XPATH, "//*[@id='header']/div/nav/div[2]/div[1]/button/span"),
        price=(By.XPATH, '//*[@id="chart-panel"]/div[1]/div[2]/div[2]/span[1]'),
        open_interest_i=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[1]/span[2]',
        ),
        open_interest_s=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[2]/span[2]',
        ),
        funding_i=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[3]/span[2]',
        ),
        funding_s=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[4]/span[2]',
        ),
        rollover=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[5]/span[2]',
        ),
    )

    # Arbitrum
    data["arbitrum"] = polygon.run(
        "https://gains.trade/trading#EUR-USD",
        need_change=True,
        path_change=[
            "//*[@id='header']/div/nav/div[2]/div[1]/button",
            '//*[@id="header"]/div/nav/div[2]/div[1]/div/div/div/button[2]',
        ],
        network=(By.XPATH, "//*[@id='header']/div/nav/div[2]/div[1]/button/span"),
        price=(By.XPATH, '//*[@id="chart-panel"]/div[1]/div[2]/div[2]/span[1]'),
        open_interest_i=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[1]/span[2]',
        ),
        open_interest_s=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[2]/span[2]',
        ),
        funding_i=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[3]/span[2]',
        ),
        funding_s=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[4]/span[2]',
        ),
        rollover=(
            By.XPATH,
            '//*[@id="chart-panel"]/div[1]/div[2]/div[3]/div/div[5]/span[2]',
        ),
    )
    polygon.close()
    data = creating_data_from_obj(file_name, data)


main("result")
