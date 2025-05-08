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

scale_selectbox = st.sidebar.selectbox("Choose case",
                                       os.listdir(path))
path /= scale_selectbox

scenario_opts = os.listdir(path)

scenarios_list = st.sidebar.multiselect("Choose scenarios to compare",
                                        scenario_opts,
                                        default = scenario_opts[0]
                       )
# metric_selectbox = st.sidebar.selectbox(
#     'Choose a metric',
#     available_metrics
# )

agg_level = st.sidebar.selectbox("Choose a spatial aggregation",
                                 aggregation_level)


@st.cache_data
def get_ba_to_state():
    c2z = pd.read_csv("data/county2zone.csv", index_col=0)
    ba_to_state = dict(zip(*c2z[['ba', 'state']].values.T))
    return ba_to_state

# @st.cache_resource
def get_data(metric):
    frames = []
    for scenario in scenarios_list:
        df = pd.read_csv(path/scenario/metric_file[metric])
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

    if agg_level == 'State':
        ba_to_state = get_ba_to_state()
        full_df = full_df.replace(ba_to_state).groupby(['i','r','t', 'scenario']).sum().reset_index()
    
    return full_df

 
# You should cache your pygwalker renderer, if you don't want your memory to explode
# @st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    with st.sidebar:
        metric_selectbox = st.selectbox(
            'Choose a metric',
            available_metrics
        )
    df = get_data(metric=metric_selectbox)
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec='./gw_config.json', spec_io_mode="rw")

if __name__ == "__main__":
    pyg_app = get_pyg_renderer()

    pyg_app.explorer()