cd /d %~dp0
call conda activate reeds-viz
streamlit run visualizer.py
