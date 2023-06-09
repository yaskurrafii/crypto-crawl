import json
from abstract import SeleniumCrawl
import time
import glob
from multiprocessing import Process
import logging

file_list = glob.glob("json/*.json")

process = [None] * len(file_list)

res = []


def getting_pair(sele: SeleniumCrawl, data_pair, data_path):
    pair_list = data_pair.get("pair_list", [])
    all_data = []
    for pair in pair_list:
        sele.change_pair_or_network(
            data_pair["by"],
            *data_pair["paths"],
            pair=pair,
            need_wait=True,
            clear_input=data_pair.get("clear", {})
        )
        data = sele.find_data(**data_path)
        all_data.append(data)
        sele.refresh()
    return all_data


def change_network(sele: SeleniumCrawl, data):
    data_network = data["network"]
    network_list = data_network["network_list"]
    for network in network_list:
        sele.change_pair_or_network(
            data_network["by"], *data_network["paths"], network=network
        )
        pair = getting_pair(sele, data["pairs"], data["data_path"])
        print(pair)


def data_process(data, file_name):
    obj = SeleniumCrawl(
        debug=True, executable_path="C:/chromedriver_win32/chromedriver.exe"
    )
    data: dict = list(data.values())[0]
    # try:
    obj.get_website(data["url"])
    additional = data.get("additional_action", False)
    if additional:
        obj.change_pair_or_network(additional["by"], *additional["path"])
    change_network(obj, data)
    obj.close()
    # except:
    #     logging.warning(f"Error in while processing file {file_name}")


if __name__ == "__main__":
    for i in range(len(file_list)):
        filed = open(file_list[i])
        datas = json.load(filed)
        process[i] = Process(target=data_process, args=[datas, file_list[i]])
        process[i].start()
