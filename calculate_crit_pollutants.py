import pandas as pd
from pathlib import Path
from os import listdir
from glob import glob
import numpy as np

if __name__ == "__main__":
    test_years = [2020]
    tolerance = 1e-0

    # runs_path = Path("C:/Users/SDotson/ReEDS-2.0/runs/runs")
    runs_path = Path(input("Please provide the path to the runs folder:"))
    tech_emit_path = Path("data/tech_emissions.xlsx")
    print("Loading technology emissions rates... ")
    emit_rate = pd.read_excel(tech_emit_path, sheet_name="emit_rate")
    scenarios_list = listdir(runs_path)


    run_list = []
    path_list = []
    for i, scenario in enumerate(scenarios_list):
        # scenario = scenarios_list[1]
        print(f"Scenario: {scenario} ({i}/{len(scenarios_list)})")
        print("Loading model outputs...")
        emit_ivrt_path = runs_path/scenario/"outputs"/"emit_irt.csv"
        gen_ivrt_path = runs_path/scenario/"outputs"/"gen_ivrt.csv"
        emit_r_path = runs_path/scenario/"outputs"/"emit_r.csv"
        try:
            emit_ivrt = pd.read_csv(emit_ivrt_path)
            gen_ivrt = pd.read_csv(gen_ivrt_path)
            emit_r = pd.read_csv(emit_r_path)
        except FileNotFoundError:
            print("Necessary file not found. Check path argument and check the model outputs exist.")
            continue

        # check if NOx and SO2 are in the model output emissions... 
        if all(crit in emit_ivrt.eall.unique() for crit in ['NOx','SO2']):
            # print('File already contains criteria pollutants! Skipping')
            # emissions are included in this scenario, move onto the next one
            continue
        else:
            merged = pd.merge(emit_rate, gen_ivrt, on=['i','v','r','t'])
            merged['emit'] = (merged['Value'] * merged['rate'])

            # print('Verifying accurate emissions calculation')
            errors = np.zeros(len(test_years))
            for i,test_year in enumerate(test_years):
                calculated_co2 = merged.loc[:,['eall','t','emit']].groupby(['eall','t']).sum().loc[('CO2',test_year)].values[0]
                modeled_co2 = emit_ivrt.loc[:,['eall','t','Value']].groupby(['eall','t']).sum().loc[('CO2',test_year)].values[0]

                rel_error = (modeled_co2-calculated_co2)/modeled_co2
                # print(f"Relative Error for {test_year}: {rel_error:.3f}")
                errors[i] = rel_error

            mean_rel_error = np.mean(errors)

            if mean_rel_error < tolerance:
                # print(f"Emissions are accurate within tolerance of {tolerance}, proceeding...")
                crit_pollutants = merged.loc[:,['eall','r','t','emit']]\
                                        .groupby(['eall','r','t'])\
                                        .sum()\
                                        .rename(columns={'emit':'Value'})\
                                        .loc[(('SO2','NOX','CO2e'), slice(None), slice(None)),:]\
                                        .reset_index()
                
                emit_r_update = pd.concat([emit_r, crit_pollutants]).drop_duplicates()
                # breakpoint()
                emit_r_update.to_csv(str(runs_path/scenario/"outputs"/"emit_r.csv"),index=False)

                run_list.append(scenario)
                path_list.append(str(runs_path/scenario))
            else:
                print(f"Mean relative error exceeds tolerance of {tolerance}, moving to next scenario.")
                print(f"Mean Relative Error: {mean_rel_error}")
                continue

    print("Creating dataframe of runs")
    scenario_df = pd.DataFrame({'run':run_list,
                                'path':path_list})
    scenario_df.to_csv('scenarios.csv')