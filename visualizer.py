from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st
from pathlib import Path
from glob import glob
import os

available_metrics = ['capacity','generation']
results_version = ['test_results','results']
available_years = ['fy25']
aggregation_level = ['BA', 'State', 'National']

metric_file = {"capacity":'cap.csv',
               "generation":'gen_ann.csv'}


# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="ReEDS Visualizer",
    layout="wide"
)
 
# Add Title
st.title("ReEDS Visualizer")


version_selectbox = st.sidebar.selectbox("Choose a version",
                                         results_version
                                         )
path = Path(f"{version_selectbox}")
year_selectbox = st.sidebar.selectbox('Choose a version year',
                                        os.listdir(path)
                                        )
path /= year_selectbox

scale_selectbox = st.sidebar.selectbox("Choose one",
                                       os.listdir(path))
path /= scale_selectbox

scenarios_list = st.sidebar.multiselect("Choose scenarios to compare",
                       os.listdir(path))

metric_selectbox = st.sidebar.selectbox(
    'Choose a metric',
    available_metrics
)

agg_level = st.sidebar.selectbox("Choose a spatial aggregation",
                                 aggregation_level)

@st.cache_resource
def get_data():
    frames = []
    for scenario in scenarios_list:
        df = pd.read_csv(path/scenario/metric_file[metric_selectbox])
        df['scenario'] = scenario
        frames.append(df)
    full_df = pd.concat(frames)
    agg_techs = ['wind-ons','wind-ofs','pv','csp','hyd', 'egs', 'coal','gas']
    for tech in agg_techs:
        if tech == ['coal', 'gas']:
            full_df.loc[(full_df['i'].str.contains(tech, case=False) & ~full_df['i'].str.contains('CCS')),'i'] = 'coal'
            full_df.loc[(full_df['i'].str.contains(tech, case=False) & full_df['i'].str.contains('CCS')),'i'] = f'{tech}_CCS'
        else:
            full_df.loc[full_df['i'].str.contains(tech, case=False), 'i'] = tech
    return full_df


# data = get_data()
 
# You should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    df = get_data()
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec='./gw_config.json', spec_io_mode="rw")

if __name__ == "__main__":
    pyg_app = get_pyg_renderer()

    pyg_app.explorer()