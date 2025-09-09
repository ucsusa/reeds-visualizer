import os
import csv

# Path to results
base_path = "./results/fy25"

# Get list of all scenario folders (exclude files)
scenario_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

# Collect all unique CSV filenames across all scenarios
csv_files = set()
for scenario in scenario_folders:
    scenario_path = os.path.join(base_path, scenario)
    for f in os.listdir(scenario_path):
        if f.endswith(".csv"):
            csv_files.add(f)

csv_files = sorted(list(csv_files))  # sort columns alphabetically

# Write summary CSV
output_file = "./analysis/results_list.csv"
with open(output_file, "w", newline="") as outcsv:
    writer = csv.writer(outcsv)

    # Header row: Scenario + filenames
    writer.writerow(["scenario"] + csv_files)

    # Rows: scenario and whether each file exists
    for scenario in scenario_folders:
        row = [scenario]
        scenario_path = os.path.join(base_path, scenario)
        existing_files = set(os.listdir(scenario_path))
        for f in csv_files:
            row.append("TRUE" if f in existing_files else "")
        writer.writerow(row)

print(f"Summary written to {output_file}")
