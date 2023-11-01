import os
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.dirname((current_script_dir))
sys.path.append(lib_path)


try:
    from src import QnA
except ImportError as e:
    print(f"Error importing dataProcessor: {e}")
else:

    question = """how To get the metamask plugin install?"""

    print(QnA.respond_to_context(question))
