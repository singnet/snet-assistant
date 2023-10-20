import json
import logging
import os
import urllib
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup


class ServiceDescription:
    def __init__(self, display_name, url="", short_description="", description=""):
        self.url = url
        self.short_description = short_description
        self.description = description
        self.display_name = display_name


class ServicesInformationGetter:
    ''' Abstract class defines interface to get information about services '''

    def __init__(self):
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.__short_descriptions = {}
        self.__full_descriptions = {}
        self.__services_documentation = {}

    @property
    @abstractmethod
    def services_descriptions(self):
        pass

    def _create_description_structure(self, display_name, description):
        url = ""
        if "url" in description:
            url = description["url"]
        short_description = ""
        if 'short_description' in description:
            short_description = description['short_description']
        description_ = ""
        if 'description' in description:
            description_ = description['description']
        return ServiceDescription(display_name, url, short_description, description_)

    def __get_documentation_from_url(self, url):
        git_host = "https://github.com"
        if git_host not in url:
            return None
        try:
            raw_url_host = "https://raw.githubusercontent.com"
            if not url.lower().endswith(".md"):
                readme_url = None
                html = urllib.request.urlopen(url).read().decode('utf8')
                bsObj = BeautifulSoup(html, 'html.parser')
                links = bsObj.find_all('a')
                for link in links:
                    if 'href' in link.attrs and link['href'].lower().endswith("readme.md"):
                        readme_url = raw_url_host + link.attrs['href'].replace("/blob/", "/")
                        break
                # if readme_url is None and 'tree' in url:
                #     readme_url = url.replace("tree", "blob") + "/README.md"
            else:
                readme_url = url
            if readme_url is not None:
                content = ""
                req = urllib.request.Request(readme_url.replace(git_host, raw_url_host).replace("/blob/", "/"))
                with urllib.request.urlopen(req) as response:
                    for line in response:
                        decoded_line = line.decode("utf-8")
                        content += decoded_line
                return content
            else:
                return None
        except Exception as ex:
            self.log.error(f"__get_documentation_from_url: Exception occurred for url {url}: {ex}")
            return None

    @property
    def short_descriptions(self):
        if len(self.__short_descriptions) == 0:
            for description in self.services_descriptions:
                self.__short_descriptions[description.display_name] = description.short_description
        return self.__short_descriptions

    @property
    def full_descriptions(self):
        if len(self.__full_descriptions) == 0:
            for description in self.services_descriptions:
                self.__full_descriptions[description.display_name] = description.description
        return self.__full_descriptions

    @property
    def services_documentation(self):
        if len(self.__services_documentation) == 0:
            for description in self.services_descriptions:
                readme_content = self.__get_documentation_from_url(description.url)
                if readme_content is not None:
                    self.__services_documentation[description.display_name] = readme_content
                elif len(description.description) >= len(description.short_description):
                    self.__services_documentation[description.display_name] = description.description
                else:
                    self.__services_documentation[description.display_name] = description.short_description
        return self.__services_documentation

    def get_service_full_descriptions(self, service_name):
        if service_name in self.full_descriptions:
            return self.full_descriptions[service_name]
        return None

    def get_service_short_descriptions(self, service_name):
        if service_name in self.short_descriptions:
            return self.short_descriptions[service_name]
        return None

    def get_service_documentation(self, service_name):
        if service_name in self.services_documentation:
            return self.services_documentation[service_name]
        return None


class JSONServicesInformationGetter(ServicesInformationGetter):
    ''' Loads information about services from json files '''

    def __init__(self, json_dir):
        super().__init__()
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.json_dir = json_dir
        self.__services_descriptions = []

    @property
    def services_descriptions(self):
        if len(self.__services_descriptions) == 0:
            for file_path in os.listdir(self.json_dir):
                # check if current file_path is a file
                json_file = os.path.join(self.json_dir, file_path)
                if os.path.isfile(json_file):
                    description = self.__load_description_from_json(json_file)
                    if description is not None:
                        self.__services_descriptions.append(description)
        return self.__services_descriptions

    def __load_description_from_json(self, json_file_path):
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    data = json.load(f)
                if ('service_description' in data) and ('display_name' in data):
                    display_name = data['display_name']
                    description = data['service_description']
                    return self._create_description_structure(display_name, description)
            return None
        except Exception as ex:
            self.log.error(f"__load_description_from_json: Exception occurred for json file {json_file_path}: {ex}")
            return None


class APIServicesInformationGetter(ServicesInformationGetter):
    ''' Loads information about services by use of post request'''

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.__services_descriptions = []

    def __load_services_info(self):
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

    @property
    def services_descriptions(self):
        if len(self.__services_descriptions) == 0:
            services_info = self.__load_services_info()
            for info in services_info:
                if 'display_name' in info:
                    description_structure = self._create_description_structure(info['display_name'], info)
                    self.__services_descriptions.append(description_structure)
        return self.__services_descriptions
