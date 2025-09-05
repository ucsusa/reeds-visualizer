import pandas as pd
import camelot
import numpy as np


if __name__ == "__main__":


    pdf_path = "data/epa_scghg_report_draft_0.pdf"
    tables = camelot.read_pdf(pdf_path, pages="87", flavor="stream")
    df = tables[0].df.loc[4:].drop(labels=[5,6])

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

    df['t'] = pd.to_datetime(df['t'], format='%Y')
    df['Value'] = df['Value'].astype('float')
    df['dr'] = df['dr'].astype('float')

    frames = []
    for e in emit_list:
        for dr in dcr_list:
            sub_df = df.loc[((df['eall']==e) & (df['dr']==dr)),:]
            sub_df = sub_df.set_index('t')
            sub_df = sub_df[['Value']].resample('YE').mean().interpolate(how='linear').assign(eall=e, dr=dr)
            sub_df = sub_df.reset_index(drop=False)
            sub_df['t'] = sub_df['t'].dt.year
            # display(sub_df)
            frames.append(sub_df)

    full_df = pd.concat(frames)
    full_df = full_df[cols]

    full_df.to_csv("data/scc_mult.csv", index=False)