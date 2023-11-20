import json
import os
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.dirname((current_script_dir))
sys.path.append(lib_path)

def answers_for_all_questions():
    filename = "prototyping/qna_Agent/platform_question_answer.json"
    json_file_path = os.path.join(filename)
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    for question in data:
        print(question['question'])
        result = QnA.respond_to_context(question['question'])
        print(result)
        print('____________________________________________________________')
        question.update({'llm_answer': result})
    json_data = json.dumps(data, indent=2)
    with open(filename, 'w') as f:
        f.write(json_data)

try:
    from src import QnA
except ImportError as e:
    print(f"Error importing dataProcessor: {e}")
else:
    print(QnA.respond_to_context("What is the name of the config file for daemon?"))
    #answers_for_all_questions()
