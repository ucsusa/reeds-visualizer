from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st
from pathlib import Path
from glob import glob
import os
import yaml

results_version = ['test_results','results']
available_years = ['fy25']
aggregation_level = ['BA', 'State', 'National']

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

metric_file = config['metric_files']
available_metrics = list(metric_file.keys())


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

# scale_selectbox = st.sidebar.selectbox("Choose case",
#                                        os.listdir(path))
# path /= scale_selectbox

scenario_opts = os.listdir(path)

scenarios_list = st.sidebar.multiselect("Choose scenarios to compare",
                                        scenario_opts,
                                        default = scenario_opts[0]
                       )

agg_level = st.sidebar.selectbox("Choose a spatial aggregation",
                                 aggregation_level)

aggregate_techs = st.sidebar.selectbox("Technology Aggregation",
                                         [True, False],
                                        # default=True,
                                         )

@st.cache_data
def get_ba_to_state():
    c2z = pd.read_csv("data/county2zone.csv", index_col=0)
    ba_to_state = dict(zip(*c2z[['ba', 'state']].values.T))
    return ba_to_state

# @st.cache_resource
def get_data(metric):
    if metric == 'Social Cost of Carbon':
        full_df = get_social_cost()
    else:
        frames = []
        for scenario in scenarios_list:
            df = pd.read_csv(path/scenario/metric_file[metric])
            df['scenario'] = scenario
            frames.append(df)
        full_df = pd.concat(frames)

        

        agg_techs = ['wind-ons','wind-ofs','pv','csp','hyd', 'egs', 'coal','gas']

        if ("i" in full_df.columns) & (aggregate_techs):
            for tech in agg_techs:
                if tech in ['coal', 'gas']:
                    # pass
                    full_df.loc[(full_df['i'].str.contains(tech, case=False) & ~full_df['i'].str.contains('CCS', case=False)),'i'] = tech
                    full_df.loc[(full_df['i'].str.contains(tech, case=False) & full_df['i'].str.contains('CCS', case=False)),'i'] = f'{tech}_CCS'
                else:
                    full_df.loc[full_df['i'].str.contains(tech, case=False), 'i'] = tech

        if agg_level == 'State':
            ba_to_state = get_ba_to_state()
            cols = list(full_df.columns)
            cols.remove("Value")
            full_df = full_df.replace(ba_to_state).groupby(cols).sum().reset_index()
        elif agg_level == "National":
            cols = list(full_df.columns)
            cols.remove("Value")
            cols.remove("r")
            full_df = full_df.groupby(cols).sum().drop(columns=['r']).reset_index()
    return full_df

def get_social_cost(metric="Social Cost of Carbon"):
    frames = []
    for scenario in scenarios_list:
        df = pd.read_csv(path/scenario/metric_file[metric])
        df['scenario'] = scenario
        frames.append(df)
    full_df = pd.concat(frames)

    if agg_level == 'State':
        cols = list(full_df.columns)
        cols.remove("ba")
        full_df = full_df.drop(columns='ba').groupby(cols).sum().reset_index()

    elif agg_level == "National":
        cols = list(full_df.columns)
        cols.remove("ba")
        full_df = full_df.drop(columns=['ba','state_abbr']).groupby(cols).sum().reset_index()

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