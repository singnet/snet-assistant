import json
import logging
import os
import urllib
from abc import abstractmethod

import pathlib
import requests
from bs4 import BeautifulSoup


class ServiceDescription:
    def __init__(self, display_name, url="", short_description="", description="", contributors = []):
        self.url = url
        self.short_description = short_description
        self.description = description
        self.display_name = display_name
        self.contributors = contributors


class ServiceGroupData:
    def __init__(self, json_data):
        self.free_calls = json_data['free_calls'] if 'free_calls' in json_data else None
        self.free_call_signer_address = json_data[
            'free_call_signer_address'] if 'free_call_signer_address' in json_data else None
        self.daemon_addresses = json_data['free_call_signer_address'] if 'free_call_signer_address' in json_data else []
        self.pricing = []
        if ('pricing' in json_data) and len(json_data['pricing']) > 0:
            for price in json_data['pricing']:
                self.pricing.append(price)
        self.endpoints = json_data['endpoints'] if 'endpoints' in json_data else []
        self.group_id = json_data['group_id'] if 'group_id' in json_data else None
        self.group_name = json_data['group_name'] if 'group_name' in json_data else None


    def __str__(self):
        return json.dumps(self.__dict__)


class ServicesInformationGetterCreator:
    @staticmethod
    def create(getter_type, json_dir=None):
        ''' json_dir  maybe should be in config'''
        if getter_type == "json":
            return JSONServicesInformationGetter(json_dir)
        if getter_type == "api":
            return APIServicesInformationGetter()
        return None


class ServicesInformationGetter:
    ''' Abstract class defines interface to get information about services '''

    def __init__(self):
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.__short_descriptions = {}
        self.__full_descriptions = {}
        self.__services_documentation = {}
        self.__display_names = []
        self.services_descriptions = []
        self.services_group_data = {}

    @abstractmethod
    def _load_services_data(self):
        pass

    def _create_description_structure(self, display_name, description, contributors_data):
        url = ""
        if "url" in description:
            url = description["url"]
        short_description = ""
        if 'short_description' in description:
            short_description = description['short_description']
        description_ = ""
        if 'description' in description:
            description_ = description['description']

        contributors = []
        if contributors_data is not None:
            for item in contributors_data:
                contributors.append(item)
        return ServiceDescription(display_name, url, short_description, description_, contributors)

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
    def display_names(self):
        if len(self.__display_names) == 0:
            for description in self.services_descriptions:
                self.__display_names.append(description.display_name)
        return self.__display_names

    @property
    def full_descriptions(self):
        if len(self.__full_descriptions) == 0:
            for description in self.services_descriptions:
                self.__full_descriptions[description.display_name] = description.description
        return self.__full_descriptions

    def _get_service_documentation_inner(self, description):
        readme_content = self.__get_documentation_from_url(description.url)
        if readme_content is not None:
            return readme_content
        elif len(description.description) >= len(description.short_description):
            return description.description
        else:
            return description.short_description

    @property
    def services_documentation(self):
        if len(self.__services_documentation) == 0:
            for description in self.services_descriptions:
                self.__services_documentation[description.display_name] = self._get_service_documentation_inner(
                    description)
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
        if not isinstance(service_name, str):
            service_name = repr(service_name).replace('"', "")
        if len(self.__services_documentation) == 0:
            for description in self.services_descriptions:
                if service_name.strip().lower() == description.display_name.strip().lower():
                    return self._get_service_documentation_inner(description)
        elif service_name in self.services_documentation:
            return self.services_documentation[service_name]
        return None

    def get_service_group_data(self, service_name):
        if service_name in self.services_group_data:
            return self.services_group_data[service_name]
        return None


class JSONServicesInformationGetter(ServicesInformationGetter):
    ''' Loads information about services from json files '''

    def __init__(self, json_dir):
        super().__init__()
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.json_dir = json_dir
        self._load_services_data()

    def download_json_data(self):
        current_dir = pathlib.Path(__file__).parent.resolve()
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        self.log.info(f"__ download_json_data: start download")
        os.system(f"sh {current_dir}/sh/load-json-data.sh {self.json_dir}")
        self.log.info(f"__download_json_data: finish download")

    def _load_services_data(self):
        files = []
        if os.path.exists(self.json_dir):
            files = os.listdir(self.json_dir)
        if len(files) == 0:
            self.download_json_data()
            files = os.listdir(self.json_dir)
        for file_path in files:
            # check if current file_path is a file
            json_file = os.path.join(self.json_dir, file_path)
            if os.path.isfile(json_file):
                # read json
                try:
                    if os.path.exists(json_file):
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                        # load data from json
                        description = self.__load_description_from_json(data)
                        if description is not None:
                            self.services_descriptions.append(description)
                            # also load group data for current service
                            if description.display_name is None:
                                return
                            self.services_group_data[description.display_name] =  \
                                ServiceGroupData(data['groups'][0]) if ('groups' in data) and (len(data['groups']) > 0) else None
                except Exception as ex:
                    self.log.error(f"__load_description_from_json: Exception occurred for json file {json_file}: {ex}")
                    return None


    def __load_description_from_json(self, data):
        if ('service_description' in data) and ('display_name' in data):
            display_name = data['display_name']
            description = data['service_description']
            contributors = []
            if "contributors" in data:
                contributors = data["contributors"]
            return self._create_description_structure(display_name, description, contributors)
        return None



class APIServicesInformationGetter(ServicesInformationGetter):
    ''' Loads information about services by use of post request'''

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self._load_services_data()

    def __request_services_info(self):
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

    def __request_groups_data(self, service):
        r = requests.get(
            f"https://marketplace-mt-v2.singularitynet.io/contract-api/org/{service['org_id']}/service/{service['service_id']}")
        data = r.json()
        if ('data' in data) and ('groups' in data['data']):
            service['groups'] = data['data']['groups']
            return service['groups'][0] if len(service['groups']) > 0 else None
        return None

    def _load_services_data(self):
        services_info = self.__request_services_info()
        for info in services_info:
            if 'display_name' in info:
                description_structure = self._create_description_structure(info['display_name'], info)
                self.services_descriptions.append(description_structure)
                if info['display_name'] is not None:
                    groups = self.__request_groups_data(info)
                    self.services_group_data[info['display_name']] = ServiceGroupData(groups)
