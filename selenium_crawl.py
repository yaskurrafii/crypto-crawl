from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class GainTradeSelenium(webdriver.Chrome):
    def __init__(self, options=Options()):
        super(GainTradeSelenium, self).__init__(options=options)

    def __website(self, url: str):
        self.get(url)
        try:
            elem = self.find_element(
                By.XPATH,
                "//*[@id='__next']/div[4]/div/div/div/div/button",
            )
            elem.click()
        except:
            pass

    def parsing_data(self, **kwargs):
        data = {}
        for name_item, values in kwargs.items():
            item = WebDriverWait(self, 30).until(EC.presence_of_element_located(values))
            data[name_item] = item.text
        return data

    def run(self, url, need_change=False, path_change=[], **kwargs):
        """
        The values in kwargs must be in tuple with (by, path)
        """

        self.__website(url)
        if need_change and path_change:
            self.change_network(path_change)
        elif need_change and not path_change:
            raise ValueError("need_change must have path_change")
        data = self.parsing_data(**kwargs)
        while data["price"] == "...":
            data = self.parsing_data(**kwargs)
        return data

    def change_network(self, path):
        if type(path) != list:
            path = [path]
        for p in path:
            network = self.find_element(By.XPATH, p)
            network.click()

    def close(self) -> None:
        return super().close()
