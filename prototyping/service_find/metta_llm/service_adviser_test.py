import json
import os

from  assistant_utils import JSONServicesInformationGetter
#import llm_gate
import hyperon as hp

def get_user_tasks(filename):
    json_file_path = os.path.join(filename)
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data


def is_correct(result:str, correct_services:str) -> bool:
    if  "[" in result:
        result = result[result.index("["):]
    if len(result) > 4 and result[0] == "[" and result[-2] == "]":
        services = result[1: - 2].split(",")
        count = 0
        services = [service.strip().replace("\"", "").lower() for service in services]
        if len(services) > 0 and len(correct_services) == 0:
            return False
        for correct in correct_services:
            if "|" in correct:
                values = correct.split("|")
            else:
                values = [correct]
            for val in values:
                if val.strip().lower() in services:
                    count += 1
                    break

        return count == len(correct_services)
    return False


if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    with open("prototyping/service_find/metta_llm/assist_operations.metta", "r") as f:
        script = f.read()
    metta = hp.MeTTa()
    metta.run(script)
    user_tasks = get_user_tasks("prototyping/service_find/llm_tests/which_service_db.json")
    correct_answers = 0
    for task in user_tasks:
        result = metta.run(f"!(respond init  () \"{task['question']}. Your reply should be very short and have a format [a, b,...], where 'a', 'b' are relevant services\")", True)
        print('---------------------------------')
        #print(result)
        task.update({'llm_answer': repr(result[0])})
        if is_correct(repr(result[0]), task["services"]):
            correct_answers += 1
        else:
            print(task)
    print(correct_answers/len(user_tasks))

    # json_data = json.dumps(user_tasks, indent=2)
    # with open("which_service_db_results.json", 'w') as f:
    #     f.write(json_data)



