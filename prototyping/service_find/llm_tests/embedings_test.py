import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
from prototyping.assistant_utils import APIServicesInformationGetter
from prototyping.service_find.llm_tests.tests_prompts import get_user_tasks
from prototyping.qna_Agent.src.QnA import distances_from_embeddings



def get_services_documentation_embeddings(documentation_dict):
    services_documentation_embeddings = {}
    for service_name, content in documentation_dict.items():
        # check if current file_path is a file
        documentation_embeddings = get_embedding(content)
        services_documentation_embeddings[service_name] = documentation_embeddings
    return services_documentation_embeddings


def search_closest_documentation(available_doc_embeddings, user_task, n=5):
    embedding = get_embedding(user_task, model='text-embedding-ada-002')
    distances = {}
    for service_name, documentation_embeddings in available_doc_embeddings.items():
        distances[service_name] = distances_from_embeddings(documentation_embeddings, embedding)
    distances = {k: v for k, v in sorted(distances.items(), key=lambda item: item[1], reverse=True)}
    return list(distances.keys())[:n]

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    emd = client.embeddings.create(input=[text], model=model)['data'][0]['embedding']
    return emd
if __name__ == '__main__':

    '''
     gets embeddings of each service documentation and finds  5 services most closest by cosine_similarity to the user's task.
     the idea of this was to use wider services description as prompt,  but use only relevant services
    '''

    json_dir_path = "../../../json"
    gen_helper = APIServicesInformationGetter()
    documentation = gen_helper.services_documentation
    services_doc_embeddings = get_services_documentation_embeddings(documentation)
    user_tasks = get_user_tasks("which_service_db.json")
    for task in user_tasks:
        result = search_closest_documentation(services_doc_embeddings, task['question'])
        task.update({'services_by_embedding': result})
    json_data = json.dumps(user_tasks, indent=2)
    with open("services_by_embeddings.json", 'w') as f:
        f.write(json_data)
    print(user_tasks[:3])
