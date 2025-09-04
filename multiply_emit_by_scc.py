import pandas as pd
from pathlib import Path
from os import listdir
from glob import glob

if __name__ == "__main__":
    test_year = 2020


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
