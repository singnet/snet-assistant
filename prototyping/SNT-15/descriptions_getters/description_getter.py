# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os.path
import json
import urllib
from bs4 import BeautifulSoup
import logging


class ServiceDescription:
    def __init__(self,  display_name, url, short_description="", description=""):
        self.url = url
        self.short_description = short_description
        self.description = description
        self.display_name = display_name


class ServiceDescriptionGetter:
    log = logging.getLogger(__name__ + '.ServiceDescriptionGetter')

    @classmethod
    def get_description(cls, json_file_path):
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    data = json.load(f)
                if ('service_description' in data) and ('display_name' in data):
                    display_name = data['display_name']
                    description = data['service_description']
                    url = None
                    if "url" in description:
                        url = description["url"]
                    short_description = None
                    if 'short_description' in description:
                        short_description = description['short_description']
                    description_ = None
                    if 'description' in description:
                        description_ = description['description']
                    if (url is not None) and (description_ is not None) and (short_description is not None):
                        return ServiceDescription(display_name, url, short_description, description_)
            return None
        except Exception as ex:
            cls.log.error(f"get_description: Exception occurred for json file {json_file_path}: {ex}")
            return None

    @classmethod
    def get_readme_text(cls, url):
        if "https://github.com" not in url:
            return ""
        try:
            if not url.lower().endswith(".md"):
                readme_url = None
                raw_url_host = "https://raw.githubusercontent.com"

                html = urllib.request.urlopen(url).read().decode('utf8')
                bsObj = BeautifulSoup(html,'html.parser')
                links = bsObj.find_all('a')
                for link in links:
                    if 'href' in link.attrs and link['href'].lower().endswith("readme.md"):
                        readme_url = raw_url_host + link.attrs['href'].replace("/blob/", "/")
                        break
                # if readme_url is None and 'tree' in url:
                #     readme_url = url.replace("tree", "blob") + "/README.md"
            else:
                readme_url = url
            content = ""
            if readme_url is not None:
                content = ""
                req = urllib.request.Request(readme_url)
                with urllib.request.urlopen(req) as response:
                    for line in response:
                        decoded_line = line.decode("utf-8")
                        content += decoded_line
        except Exception as ex:
            cls.log.error(f"get_readme_text: Exception occurred for url {url}: {ex}")
            return ""
        return content

if __name__ == '__main__':
    dir_path = "../../../json"
    count = 0
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        json_file = os.path.join(dir_path, file_path)
        if os.path.isfile(json_file):
            description = ServiceDescriptionGetter.get_description(json_file)
            if description is not None:
                readme_content = ServiceDescriptionGetter.get_readme_text(description.url)
                if readme_content != "":
                    #print(json_file)
                    count = count + 1
                elif "https://github.com" in description.url:
                    print("no git readme:", description.url)
                else:
                    print("no git:", description.url)
    print(count)


