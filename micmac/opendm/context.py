import os
import multiprocessing

# Define some needed locations
scripts_path = os.path.abspath(os.path.dirname(__file__))
root_path, _ = os.path.split(scripts_path)

settings_path = os.path.join(root_path, 'settings.yaml')

# Define the number of cores
num_cores = multiprocessing.cpu_count()