from glob import glob
import os
from pathlib import Path
import sys
import argparse
import subprocess
import shutil
import yaml

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

metric_file = config['metric_files']

if __name__ == "__main__":

    search_path = Path("C:/Users/SDotson/ReEDS-2.0/runs/final_runs/")
    # search_path = Path("C:/Users/SDotson/ReEDS-2.0/runs/penultimate_runs/")

    # target_path = Path("./test_results/move_test")
    target_path = Path("./results/fy25/")
    # target_path.mkdir(exist_ok=True, parents=True)

    for dir in os.listdir(search_path):
        print(f"[{dir}]")
        for file in metric_file.values():
            # print(file)
            original_path = search_path/dir/"outputs"/file
            # print(original_path)
            if original_path.exists():
                new_dir = dir.strip('_')
                tpath = target_path/new_dir
                tpath.mkdir(exist_ok=True, parents=True)
                print(f"Copying {file} to {tpath}")
                shutil.copy(original_path, tpath/file)
