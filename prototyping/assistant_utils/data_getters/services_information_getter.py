import json
import logging
import os
import urllib
from abc import abstractmethod
import concurrent.futures
import pathlib
import requests
from bs4 import BeautifulSoup


class ServiceDescription:
    def __init__(self, display_name, url="", short_description="", description="", contributors=[]):
        self.url = url
        self.short_description = short_description
        self.description = description
        self.display_name = display_name
        self.contributors = contributors

class ServicesInformationGetterCreator:
    @staticmethod
    def create(json_dir=None):
        ''' json_dir  maybe should be in config'''
        if not os.path.exists(json_dir):
            os.mkdir(json_dir)
        if len(os.listdir(json_dir)) > 0:
            return JSONServicesInformationGetter(json_dir)
        else:
            return APIServicesInformationGetter(json_dir)


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
        self.raw_url_host = "https://raw.githubusercontent.com"
        self.git_host = "https://github.com"
        self.api_host = 'https://api.github.com/repos'
        api_token = os.environ["GIT_TOKEN"]
        self.headers = {'Authorization': 'token %s' % api_token}

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


    def __parse_page(self, url):
        '''
        find link to readme on page with use of BeautifulSoup
        '''
        readme_url = None
        html = urllib.request.urlopen(url).read().decode('utf8')
        bsObj = BeautifulSoup(html, 'html.parser')
        links = bsObj.find_all('a')
        for link in links:
            if 'href' in link.attrs and link['href'].lower().endswith("readme.md"):
                readme_url = self.raw_url_host + link.attrs['href'].replace("/blob/", "/")
                break
        return readme_url

    def __load_git_contents(self, url):
        '''
        use git api to find link to readme
        '''
        repo_name = url[url.find(self.git_host) + len(self.git_host):]
        readme_url = None
        url = self.api_host + repo_name + "/contents"
        result = requests.get(url, headers=self.headers)
        result = json.loads(result.text)
        if len(result) > 0:
            for res_dict in result:
                if ("html_url" in res_dict) and str(res_dict["html_url"]).lower().endswith("readme.md"):
                    readme_url = res_dict["html_url"]
                    break
        return readme_url

    def __get_documentation_from_url(self, url:str):
        # ToDo  need to read documentation from url like https://singnet.github.io/dnn-model-services/users_guide/i3d-video-action-recognition.html

        if self.git_host not in url:
            return None
        try:

            if not url.lower().endswith(".md"):
                # readme_url = self.__parse_page(url)
                # if readme_url is None:
                readme_url = self.__load_git_contents(url)
                if (readme_url is None) and ('tree' in url):
                    readme_url = url.replace("tree", "blob") + "/README.md"
            else:
                readme_url = url
            if readme_url is not None:
                content = ""
                req = urllib.request.Request(readme_url.replace(self.git_host, self.raw_url_host).replace("/blob/", "/"))
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

    def load_groups_data(self, data):
        group_data = []
        for group in data:
            group_data.append(group)
        return group_data



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
                            if ('groups' in data) and (len(data['groups']) > 0):
                                self.services_group_data[description.display_name] = self.load_groups_data(data['groups'])
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

    def __init__(self, json_dir):
        super().__init__()
        self.json_dir = json_dir
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

    def __create_json(self,  info,   service_description_keys):
        if 'display_name' in info:
            contributors = info["contributors"] if "contributors" in info else None
            description_structure = self._create_description_structure(info['display_name'], info, contributors)
            self.services_descriptions.append(description_structure)
            if info['display_name'] is not None:
                groups = self.__request_groups_data(info)
                info['groups'] = groups if isinstance(groups, list) else [groups]
                self.services_group_data[info['display_name']] = self.load_groups_data(info['groups'])
            info["service_description"] = {key: info[key] for key in service_description_keys}
            for key in service_description_keys:
                info.pop(key)
            filename = os.path.join(self.json_dir, f"{info['display_name']}.json")
            with open(filename, 'w') as f:
                json_object = json.dumps(info, indent=3)
                f.write(json_object)

    def _load_services_data(self):
        services_info = self.__request_services_info()
        service_description_keys = ["url", "short_description", "description"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for info in services_info:
                executor.submit(self.__create_json,  info=info,
                                               service_description_keys=service_description_keys)



