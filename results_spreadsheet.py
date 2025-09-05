import os
import pandas as pd
from tqdm import tqdm

# Paths
base_path = "./results/fy25"
summary_file = "./analysis/results_list.csv"
output_excel = "./analysis/results_spreadsheet.xlsx"
mapping_file = "./data/county2zone.csv"

# Technologies to collapse
agg_techs = ['wind-ons','wind-ofs','pv','csp','hyd','egs','coal','gas']

# === Helpers ===
def load_region_map(path):
    df = pd.read_csv(path)
    if "ba" in df.columns and "r" not in df.columns:
        df = df.rename(columns={"ba": "r"})
    return df.set_index("r")["state"].to_dict()

def clean_and_aggregate(df, scenario, region_to_state):
    # Normalize headers
    df.columns = df.columns.str.strip().str.lower()

    # r -> state
    if "r" in df.columns:
        df["state"] = df["r"].map(region_to_state)
        df = df.drop(columns=["r"])

    # collapse i
    if "i" in df.columns:
        df["i"] = df["i"].astype(str).str.strip().str.lower()
        for tech in agg_techs:
            if tech in ["coal", "gas"]:
                df.loc[df["i"].str.contains(tech, case=False, na=False) & ~df["i"].str.contains("ccs", case=False, na=False), "i"] = tech
                df.loc[df["i"].str.contains(tech, case=False, na=False) & df["i"].str.contains("ccs", case=False, na=False), "i"] = f"{tech}_ccs"
            else:
                df.loc[df["i"].str.contains(tech, case=False, na=False), "i"] = tech

    # add Scenario
    df.insert(0, "scenario", scenario)

    # aggregate value
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        group_cols = [c for c in df.columns if c != "value"]
        df = df.groupby(group_cols, as_index=False)["value"].sum()
    else:
        df = df.drop_duplicates()

    return df

# === Main ===
summary_df = pd.read_csv(summary_file)
region_to_state = load_region_map(mapping_file)
csv_types = [c for c in summary_df.columns if c.lower() != "scenario"]

tabs = {csv_name: [] for csv_name in csv_types}

# Wrap scenario loop in tqdm progress bar
for _, row in tqdm(summary_df.iterrows(), total=len(summary_df), desc="Processing scenarios"):
    scenario = row["Scenario"]
    for csv_name in csv_types:
        csv_path = os.path.join(base_path, scenario, csv_name)
        if not os.path.exists(csv_path):
            continue
        try:
            df = pd.read_csv(csv_path)
            df = clean_and_aggregate(df, scenario, region_to_state)
            tabs[csv_name].append(df)
        except Exception as e:
            print(f"Error processing {csv_path}: {e}")

# === Write Excel ===
total_rows = 0
for dfs in tabs.values():
    if dfs:
        total_rows += sum(len(df) for df in dfs)
print(f"\nTotal rows across all sheets: {total_rows:,}\n")
with pd.ExcelWriter(output_excel, engine="xlsxwriter") as writer:
    for csv_name, dfs in tqdm(tabs.items(), desc="Writing Excel"):
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            sheet_name = os.path.splitext(csv_name)[0][:31]
            combined.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\nWrote {output_excel}")
