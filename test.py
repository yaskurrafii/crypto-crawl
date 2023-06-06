import json
from abstract import SeleniumCrawl
import time

json_file = open("data.json")
data = json.load(json_file)

res = []

for key, value in data.items():
    obj = SeleniumCrawl()
    obj.get_website(value["url"])
    additional = value.get("additional_action", False)
    if additional:
        obj.change_pair_or_network(additional["by"], *additional["path"])

    wait_loader = value.get("wait_loader", "")
    data_path = value.get("data_path", {})
    pairs = value.get("pairs")
    networks = value.get("network")

    for network in networks.get("network_list"):
        obj.change_pair_or_network(
            networks.get("by"), *networks.get("paths"), network=network
        )
        for pair in pairs.get("pair_list", []):
            obj.change_pair_or_network(
                pairs.get("by", "xpath"),
                *pairs.get("paths", ""),
                pair=pair,
                need_wait=True
            )
            data = obj.find_data(**data_path)
            res.append(data)
    time.sleep(1)
    obj.close()

print(res)
