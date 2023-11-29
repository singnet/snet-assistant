import json
import os


import hyperon as hp
from prototyping.metta_llm.metta_llm_functions.service_adviser_test import is_correct
from prototyping.metta_llm.metta_guidance.runner import run_script

types = {}
types['services'] = "prototyping/metta_llm/metta_guidance/which_service_db.json"
types['snet'] = "prototyping/metta_llm/metta_guidance/platform_question_answer.json"
types['specificservice'] = "prototyping/metta_llm/metta_guidance/service_question.json"

def get_user_tasks(filename):
    json_file_path = os.path.join(filename)
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data


def detect_question_type(type_name, filename):
    run_script("prototyping/metta_llm/metta_guidance/question_types_guidance.metta", metta)
    user_tasks = get_user_tasks(filename)
    correct_answers = 0
    for task in user_tasks:
        result = metta.run(f"!(question-type \"{task['question']}\")", True)
        print(result)
        if type_name in repr(result[1]).lower():
            correct_answers += 1
    print(type_name, correct_answers/len(user_tasks))


def detect_all_question_types():
    for k, v in types.items():
        detect_question_type(k, v)

def answer_specific_service_question():
    run_script("prototyping/metta_llm/metta_guidance/question_types_guidance.metta", metta)

    service_questions = get_user_tasks(types['specificservice'])
    count = 0
    for task in service_questions:
        result = metta.run(f"!(respond \"{task['question']}\")", True)
        count += 1
        print(count)
        print("llm answer:", result)
        print("correct answer:", task["answer"])

def answer_platform_question():
    run_script("prototyping/metta_llm/metta_guidance/question_types_guidance.metta", metta)
    service_questions = get_user_tasks(types['snet'])
    for task in service_questions:
        q_type = metta.run(f"!(question-type \"{task['question']}\")", True)
        result = metta.run(f"!(respond \"{task['question']}\")", True)
        task.update({'gpt3_answer': repr(result[1])})
        task.update({'question type': repr(q_type[1])})
        print(result)
        print("______________________________")
    json_data = json.dumps(service_questions, indent=2)
    with open(types['snet'], 'w') as f:
        f.write(json_data)

def suggest_service():
    run_script("prototyping/metta_llm/metta_guidance/service_finder_guidance.metta", metta)
    questions = get_user_tasks(types["services"])
    count = 0
    correct = 0
    for task in questions:
        metta.run(f"!(change-state! (user-question) (\"{task['question']}\"))", True)
        result = metta.run("!(llm (messages))")
        count += 1
        if is_correct(repr(result[0][0]), task["services"]):
            correct += 1
        else:
            print(repr(result[0][0]), " ", task["services"])
            print("______________________________")
    if correct > 0:
        print(correct / count)

if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    metta_motto_path = os.environ["METTAMOTOPATH"]
    env_builder = hp.Environment.custom_env(include_paths=[metta_motto_path])
    metta = hp.MeTTa(env_builder=env_builder)
    detect_all_question_types()
    #answer_specific_service_question()
    #suggest_service()
    #answer_platform_question()




# . Your reply should be very short and have a format [a, b,...], where 'a', 'b' are relevant services
