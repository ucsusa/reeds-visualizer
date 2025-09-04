import pandas as pd
from pathlib import Path
from os import listdir
from glob import glob

if __name__ == "__main__":
    test_year = 2020

    # runs_path = Path("C:/Users/SDotson/ReEDS-2.0/runs/runs")
    runs_path = Path(input("Please provide the path to the runs folder:"))
    tech_emit_path = Path("C:/Users/SDotson/ReEDS-2.0/runs/tech_emissions.xlsx")
    print("Loading technology emissions rates... ")
    emit_rate = pd.read_excel(tech_emit_path, sheet_name="emit_rate")
    scenarios_list = listdir(runs_path)


    run_list = []
    path_list = []
    for i, scenario in enumerate(scenarios_list):
        # scenario = scenarios_list[1]
        print(f"Scenario: {scenario} ({i}/{len(scenarios_list)})")
        print("Loading model outputs...")
        emit_r_path = runs_path/scenario/"outputs"/"emit_r.csv"
        try:
             # Read emit_r.csv
             emit_r = pd.read_csv(emit_r_path)
        except FileNotFoundError:
            print("Necessary file not found. Check path argument and check the model outputs exist.")
            continue

# Read the SCC multipliers
scc_mult = pd.read_excel('scc.xlsx')

# Ensure column names are consistent (case-insensitive match)
emit_r.columns = emit_r.columns.str.lower()
scc_mult.columns = scc_mult.columns.str.lower()

# Merge on 'eall' and 't' columns
merged = pd.merge(
    emit_r,
    scc_mult,
    on=['eall', 't'],
    suffixes=('_emit', '_scc')
)

# Multiply the values
merged['product'] = merged['value_emit'] * merged['value_scc']

# Output the result
merged.to_csv('scc_values.csv', index=False)

print('Multiplication complete. Output saved to scc_values.csv')
