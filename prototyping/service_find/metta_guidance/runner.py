import json
import os

# import llm_gate
import hyperon as hp


def get_user_tasks(filename):
    json_file_path = os.path.join(filename)
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    # "prototyping/service_find/metta_guidance/service_finder_guidance.metta"
    # "prototyping/service_find/metta_guidance/question_types_guidance.metta"
    with open("prototyping/service_find/metta_guidance/question_types_guidance.metta", "r") as f:
        script = f.read()
    env_builder = hp.Environment.custom_env(
        include_paths=["/media/sveta/hdisk4/singnet/hyperon-experimental/python/sandbox/neurospace"])
    metta = hp.MeTTa(env_builder=env_builder)
    print(metta.run(script))
    # user_tasks = get_user_tasks("prototyping/service_find/llm_tests/which_service_db.json")
    # platform_questions = get_user_tasks("prototyping/service_find/metta_guidance/platform_question.json")
    # correct_answers = 0
    # for task in user_tasks[:3]:
    #     metta.run(f"!(change-state! (user-question) (\"{task['question']}\"))", True)
    #     result = metta.run("!(llm (question-type-messages))", True)
    #     print(result)
    #     if 'services' in repr(result[0]).lower():
    #         correct_answers += 1
    # print("service", correct_answers/len(user_tasks))
    # correct_answers = 0
    # for task in platform_questions[:3]:
    #     metta.run(f"!(change-state! (user-question) (\"{task['question']}\"))", True)
    #     result = metta.run("!(llm (question-type-messages))", True)
    #     print(result)
    #     if 'snet' in repr(result[0]).lower():
    #         correct_answers += 1
    # print("platform", correct_answers / len(platform_questions))



# . Your reply should be very short and have a format [a, b,...], where 'a', 'b' are relevant services
