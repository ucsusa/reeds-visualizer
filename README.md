# reeds-visualizer
A Tableau-like platform for visualizing data from the ReEDS model leveraging [`PyGWalker`](https://kanaries.net/pygwalker)
and [`streamlit`](https://docs.streamlit.io/).

![Screenshot of visualizer](images/visualizer-screenshot.png)

# Requirements

Users must have the following installed:

- [git](https://git-scm.com/downloads)
- A python distribution ([Anaconda](https://www.anaconda.com/download/success) or [Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html))

# Environment Set Up

1. Open a terminal window (terminal on a Unix system or Command Prompt on Windows).

2. Clone the repository by typing (or copy-pasting) the following command:

```bash
git clone https://github.com/ucsusa/reeds-visualizer.git
```

3. Navigate into the newly created directory with
```bash
cd reeds-visualizer
```

4. Create a new Python environment with (and follow the prompts)
```bash
conda env create
```

5. Activate the newly created Python environment
```bash
conda activate reeds-viz
```

6. Start the visualizer, which will open a new browser window, using
```bash
streamlit run visualizer.py
```

# Pulling recent changes

When issues or tickets lead to code changes, those changes will not automatically be present on
a local copy of the repository. 

In order to pull down the changes, make sure you are the in `reeds-visualizer` working directory
in your command prompt or terminal window. Then you can use the following command (assuming the desired changes are on the main branch):

```bash
git pull origin main
```

> [!NOTE]
> You cannot pull changes or execute any commands in the same session that is running the visualizer.
> In other words, you must shut down the visualizer, pull the changes, and restart it for the changes to take effect.

# Compiling results into a spreadsheet for analysis

There are two scripts which can be run sequentially to aid in analyzing results.

1. **Run `results_list.py` to create a matrix of results**, with rows for scenarios and columns for metrics (generation, capacity, emissions, etc). "TRUE" indicates that an output file exists for the given combination of scenario and metric.
2. **Edit `analysis/results_list.csv` to limit which files will be included in the final spreadsheet.** This can be acomplished by deleting entire rows/columns, and/or deleting "TRUE" from specific combinations that aren't needed. Limiting which files are included will greatly reduce the processing time and the file size of the final result. Very large files may be unstable.
3. **Run results_spreadsheet.py to create a spreadsheet with the desired results.** If there is an existing version of `results_spreadsheet.xlsx`, the script will append it, and overwrite existing sheets. Otherwise, a new copy will be created.
