import os
import pandas as pd
from tqdm import tqdm

# Paths
base_path = "./results/fy25"
summary_file = "./analysis/results_list.csv"
output_excel = "./analysis/results_spreadsheet.xlsx"
mapping_file = "./data/county2zone.csv"

# Technologies to collapse
agg_techs = ["wind-ons", "wind-ofs", "pv", "csp", "hyd", "egs", "coal", "gas"]


# === Helpers ===
def load_region_map(path):
    df = pd.read_csv(path)
    if "ba" in df.columns and "r" not in df.columns:
        df = df.rename(columns={"ba": "r"})
    return df.set_index("r")["state"].to_dict()


def clean_and_aggregate(df, scenario, region_to_state):
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Normalize headers
    df.columns = df.columns.str.strip().str.lower()

    # Drop 'ba' if present
    if "ba" in df.columns:
        df = df.drop(columns=["ba"])

    # Map 'r' to state
    if "r" in df.columns:
        df["state"] = df["r"].map(region_to_state)
        df = df.drop(columns=["r"])

    # Map 'rr' to state2
    if "rr" in df.columns:
        df["state2"] = df["rr"].map(region_to_state)
        df = df.drop(columns=["rr"])

    # collapse i
    if "i" in df.columns:
        df["i"] = df["i"].astype(str).str.strip().str.lower()
        for tech in agg_techs:
            if tech in ["coal", "gas"]:
                df.loc[
                    df["i"].str.contains(tech, case=False, na=False)
                    & ~df["i"].str.contains("ccs", case=False, na=False),
                    "i",
                ] = tech
                df.loc[
                    df["i"].str.contains(tech, case=False, na=False)
                    & df["i"].str.contains("ccs", case=False, na=False),
                    "i",
                ] = f"{tech}_ccs"
            else:
                df.loc[df["i"].str.contains(tech, case=False, na=False), "i"] = tech

    # add Scenario
    df.insert(0, "scenario", scenario)

    # aggregate value
    # Identify numeric columns to aggregate
    health_cols = ["tons", "md", "damage_$", "mortality"]

    if "value" in df.columns:
        agg_cols = ["value"]
    elif set(health_cols).issubset(df.columns):
        agg_cols = health_cols
    else:
        agg_cols = []

    if agg_cols:
        # Group by all non-aggregated columns
        group_cols = [c for c in df.columns if c not in agg_cols]
        df = df.groupby(group_cols, as_index=False)[agg_cols].sum()
    else:
        df = df.drop_duplicates()

    return df


# === Main ===
summary_df = pd.read_csv(summary_file)
region_to_state = load_region_map(mapping_file)
csv_types = [c for c in summary_df.columns if c.lower() != "scenario"]

tabs = {csv_name: [] for csv_name in csv_types}

# Wrap scenario loop in tqdm progress bar
for _, row in tqdm(
    summary_df.iterrows(), total=len(summary_df), desc="Processing scenarios"
):
    scenario = row["scenario"]
    for csv_name in csv_types:
        csv_path = os.path.join(base_path, scenario, csv_name)
        try:
            df = pd.read_csv(csv_path)
            df = clean_and_aggregate(df, scenario, region_to_state)
            tabs[csv_name].append(df)
        except FileNotFoundError as e:
            print(f"Error processing {csv_path}: {e}")
# === Write Excel ===
total_rows = 0
for dfs in tabs.values():
    if dfs:
        total_rows += sum(len(df) for df in dfs)
print(f"\nTotal rows across all sheets: {total_rows:,}\n")

if os.path.exists(output_excel):
    # Must use openpyxl for append mode
    excel_engine = "openpyxl"
    mode = "a"
    if_exists = "replace"
    print(f"Updating existing file: {output_excel}")
else:
    # Prefer the faster xlsxwriter for new files, fall back to openpyxl
    try:
        import xlsxwriter
        excel_engine = "xlsxwriter"
    except ImportError:
        excel_engine = "openpyxl"
        print("xlsxwriter not found, using openpyxl")
    mode = "w"
    if_exists = None
    print(f"Creating new file: {output_excel}")

with pd.ExcelWriter(
    output_excel,
    engine=excel_engine,
    mode=mode,
    if_sheet_exists=if_exists
) as writer:
    for csv_name, dfs in tqdm(tabs.items(), desc="Writing XLSX", unit="sheet"):
        dfs = [df for df in dfs if not df.empty]
        if not dfs:
            continue
        combined = pd.concat(dfs, ignore_index=True)
        sheet_name = csv_name.replace(".csv", "")[:31]
        combined.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\nWrote {output_excel}")
