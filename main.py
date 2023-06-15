import json
from abstract import SeleniumCrawl
import time
import glob
from multiprocessing import Pool
import logging

file_list = glob.glob("json/*.json")

process = [None] * len(file_list)

res = []


def getting_pair(sele: SeleniumCrawl, data_pair, data_path, network):
    pair_list = data_pair.get("pair_list", [])
    data_include = [
        "price",
        "network",
        "open_interest_i",
        "open_interest_s",
        "funding_i",
        "funding_s",
        "rollover",
    ]
    all_data = []
    if not data_pair.get("pair_list", True):
        raise ValueError("Do not have pair_list")
    for pair in pair_list:
        sele.change_pair_or_network(
            data_pair["by"],
            *data_pair["paths"],
            pair=pair,
            need_wait=True,
            clear_input=data_pair.get("clear", {}),
        )
        data = sele.find_data(**data_path)
        for i in data_include:
            if i not in list(data.keys()):
                data[i] = "-"
        data["network"] = network
        data["pair"] = pair
        all_data.append(data)
        sele.refresh()
    return all_data


def change_network(sele: SeleniumCrawl, data):
    data_network = data["network"]
    network_list = data_network["network_list"]
    res
    for network in network_list:
        sele.change_pair_or_network(
            data_network["by"], *data_network["paths"], network=network
        )
        pair = getting_pair(sele, data["pairs"], data["data_path"], network)
        res.append(pair)
    return {"data": res}


def writing_result(data: dict, file_path):
    if "\\" in file_path:
        file_name = file_path.split("\\")[-1]
        file_name = f"output/{file_name}"
    else:
        file_name = file_path
    with open(f"{file_name}", "w") as f:
        f.write(json.dumps(data))


def data_process(file_name):
    filed = open(file_name)
    data = json.load(filed)
    obj = SeleniumCrawl(debug=True)
    data: dict = list(data.values())[0]
    try:
        obj.get_website(data["url"])
        additional = data.get("additional_action", False)
        if additional:
            obj.change_pair_or_network(additional["by"], *additional["path"])
        res = change_network(obj, data)
        obj.close()
        writing_result(res, file_name)

    except:
        logging.warning(f"Error in while processing file {file_name}")
        obj.close()


if __name__ == "__main__":
    pool = Pool(processes=2)
    pool.map(data_process, file_list)
    pool.close()
    pool.join()
