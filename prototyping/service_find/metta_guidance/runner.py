import json
import os

# import llm_gate

import hyperon as hp


def get_user_tasks(filename):
    json_file_path = os.path.join(filename)
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data


def detect_question_type( type_name, filename):
    #user_tasks = get_user_tasks("prototyping/service_find/llm_tests/which_service_db.json")
    user_tasks = get_user_tasks(filename)
    correct_answers = 0
    for task in user_tasks[:3]:
        result = metta.run(f"!(question-type \"{task['question']}\")", True)
        print(result)
        if type_name in repr(result[1]).lower():
            correct_answers += 1
    print(type_name, correct_answers/len(user_tasks))


def detect_all_question_types():
    types = {}
    types['services'] = "prototyping/service_find/llm_tests/which_service_db.json"
    types['snet'] = "prototyping/service_find/metta_guidance/platform_question.json"
    types['specificservice'] = "prototyping/service_find/metta_guidance/service_question.json"
    for k, v in types.items():
        detect_question_type(k, v)

def answer_specific_service_question():
    service_questions = get_user_tasks("prototyping/service_find/metta_guidance/service_question.json")
    count = 0
    for task in service_questions:
        result = metta.run(f"!(respond \"{task['question']}\")", True)
        count += 1
        print(count)
        print("llm answer:", result)
        print("correct  answer:", task["answer"])


if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    # "prototyping/service_find/metta_guidance/service_finder_guidance.metta"
    # "prototyping/service_find/metta_guidance/question_types_guidance.metta"
    with open("prototyping/service_find/metta_guidance/question_types_guidance.metta", "r") as f:
        script = f.read()
    env_builder = hp.Environment.custom_env(
        include_paths=["/media/sveta/hdisk4/singnet/metta-motto/motto"])
    metta = hp.MeTTa(env_builder=env_builder)
    print(metta.run(script))
    #detect_all_question_types()
    answer_specific_service_question()




# . Your reply should be very short and have a format [a, b,...], where 'a', 'b' are relevant services
