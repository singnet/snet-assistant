import os
import sys


current_script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = (os.path.dirname((current_script_dir)))
sys.path.append(lib_path)


try:
   from src import summary
except ImportError as e:
    print(f"Error importing dataProcessor: {e}")
else:
    """Load dataset, generate summaries, and save to a JSON file."""
    summary.save_summary()
