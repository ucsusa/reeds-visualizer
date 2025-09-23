import pandas as pd
import camelot
import numpy as np
import yaml


if __name__ == "__main__":


    pdf_path = "data/epa_scghg_report_draft_0.pdf"
    tables = camelot.read_pdf(pdf_path, pages="126", flavor="stream")
    df = tables[0].df.loc[8:]

    dcr_list = [2.5, 2, 1.5]
    emit_list = ["CO2", "CH4", "N2O"]

    df = df.set_index(0)
    df.columns = pd.MultiIndex.from_product([emit_list, dcr_list])
    df = df.reset_index().drop(labels=[0,1,2]).set_index(0)
    df.index.name = 't'
    df = df.replace(to_replace=',', value='', regex=True)

    df = df.unstack().to_frame().reset_index()
    cols = ['eall','dr','t','Value']
    df.columns = cols

    df['t'] = pd.to_datetime(df['t'], format='%Y').dt.year
    df['Value'] = df['Value'].astype('float')
    df['dr'] = df['dr'].astype('float')



    # add discount factor column

    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)

    analysis_year = int(config['analysis_year'])


    d_tau = lambda r, tau: 1 / (1+r)**tau

    df['dtau'] = d_tau(df['dr']/100, df['t']-analysis_year)


    df.to_csv("data/scc_mult.csv", index=False)