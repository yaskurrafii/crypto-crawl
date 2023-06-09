import json
from abstract import SeleniumCrawl
import time
import glob
from multiprocessing import Process

file_list = glob.glob("json/*.json")

process = [None] * len(file_list)

res = []


def data_process(data):
    obj = SeleniumCrawl(
        debug=True, executable_path="C:/chromedriver_win32/chromedriver.exe"
    )
    data: dict = list(data.values())[0]
    obj.get_website(data["url"])
    additional = data.get("additional_action", False)
    if additional:
        obj.change_pair_or_network(additional["by"], *additional["path"])


if __name__ == "__main__":
    for i in range(len(file_list)):
        filed = open(file_list[i])
        datas = json.load(filed)
        process[i] = Process(target=data_process, args=[datas])
        process[i].start()
