import json
import os

import openai

from prototyping.service_find.llm_tests.prompt_generator_helper import PromptGeneratorHelper
from prototyping.service_find.llm_tests.tests_prompts import get_user_tasks
from openai.embeddings_utils import cosine_similarity

openai.api_key = os.environ["OPENAI_API_KEY"]


def get_services_documentation_embeddings(documentation_dict):
    services_documentation_embeddings = {}
    for service_name, content in documentation_dict.items():
        # check if current file_path is a file
        documentation_embeddings = PromptGeneratorHelper.get_embedding(content)
        services_documentation_embeddings[service_name] = documentation_embeddings
    return services_documentation_embeddings


def search_closest_documentation(available_doc_embeddings, user_task, n=5):
    embedding = PromptGeneratorHelper.get_embedding(user_task, model='text-embedding-ada-002')
    distances = {}
    for service_name, documentation_embeddings in available_doc_embeddings.items():
        distances[service_name] = cosine_similarity(documentation_embeddings, embedding)
    distances = {k: v for k, v in sorted(distances.items(), key=lambda item: item[1], reverse=True)}
    return list(distances.keys())[:n]


if __name__ == '__main__':
    json_dir_path = "../../../json"
    gen_helper = PromptGeneratorHelper(json_dir_path)
    documentation = gen_helper.get_services_documentation()
    services_doc_embeddings = get_services_documentation_embeddings(documentation)
    user_tasks = get_user_tasks("which_service_db.json")
    for task in user_tasks:
        result = search_closest_documentation(services_doc_embeddings, task['question'])
        task.update({'services_by_embedding': result})
    json_data = json.dumps(user_tasks, indent=2)
    with open("services_by_embeddings.json", 'w') as f:
        f.write(json_data)
    print(user_tasks[:3])
