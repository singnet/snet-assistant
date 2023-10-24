# Define the URL of the ZIP archive
# import src

import os
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(os.path.dirname((current_script_dir)), 'src')
sys.path.append(lib_path)
print(sys.path)


try:
    import dataProcessor
except ImportError as e:
    print(f"Error importing dataProcessor: {e}")
else:
    repo_url = 'https://github.com/singnet/dev-portal/archive/refs/heads/master.zip'

    # Create an instance of DataProcessor
    processor = dataProcessor.DataProcessor(repo_url)
