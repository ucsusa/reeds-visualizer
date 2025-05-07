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


