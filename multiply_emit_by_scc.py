import pandas as pd
from pathlib import Path
from os import listdir
from glob import glob

if __name__ == "__main__":

    scenarios = listdir('results/fy25')
    scc = pd.read_csv("data/scc_mult.csv")

    for i, scenario in enumerate(scenarios):
        emit_irt_path = Path(f'results/fy25/{scenario}/emit_irt.csv')
        try:
            temp_file = pd.read_csv(emit_irt_path)
        except FileNotFoundError:
            print(f"File not found: {emit_irt_path}")
            continue
        df = temp_file.drop(columns=['i']).groupby(['eall', 'r','t']).sum().reset_index()

        # Merge on 'eall' and 't' columns
        merged = pd.merge(
            df,
            scc,
            on=['eall', 't'],
            suffixes=('_emit', '_scc')
        )
        # Multiply the values
        merged['Value'] = merged['Value_emit'] * merged['Value_scc']
        merged = merged.drop(columns=['Value_emit','Value_scc'])
        # Output the result
        scc_path = Path(f'results/fy25/{scenario}/scc_values.csv')
        merged.to_csv(scc_path, index=False)


