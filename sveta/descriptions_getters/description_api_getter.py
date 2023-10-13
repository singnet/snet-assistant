# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import time
import requests

def get_services_info():
    r = requests.post("https://marketplace-mt-v2.singularitynet.io/contract-api/service", json={
        "q": "",
        'limit': 80,
        "offset": 0,
        "total_count": 0,
        "s": "all",
        "sort_by": "ranking",
        "order_by": "asc",
        "filters": []})
    data = r.json()
    if ("data" in data) and ('result' in data['data']):
        return data["data"]['result']
    return None

def add_groups(service):
    r = requests.get(
        f"https://marketplace-mt-v2.singularitynet.io/contract-api/org/{service['org_id']}/service/{service['service_id']}")
    data = r.json()
    if ('data' in data) and ('groups' in data['data']):
        service['groups'] = data['data']['groups']


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start = time.time()
    services = get_services_info()
    print("all services:", time.time() - start)
    print(len(services))
    start = time.time()
    add_groups(services[79])
    print("add group for one service", time.time() - start)
    print(services[79])



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
