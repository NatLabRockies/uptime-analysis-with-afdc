# Uptime Analysis using ALternative Fuels Data Center (AFDC) data

This repo includes the analysis code used for the uptime analysis. 

The code in this repo is runnable using a small subset of the Alternative Fuels Data Center charging station data provided in the repo (one week of data, for January 1-7, 2023). The full data used in this analysis can be downloaded from the Alternative Fuels Data Center website (https://afdc.energy.gov/data_download).

## Instructions for running

1. Install [pixi](https://pixi.sh/latest/#installation).
2. From the repo root, run all steps on the example data:

   ```bash
   pixi run plots
   ```

   This installs the Python and R environment on first use, then runs each step in order:

   | Step | Task | Script | Output |
   | --- | --- | --- | --- |
   | 1. Clean data | `pixi run clean-data` | `data_cleaning/clean_data_for_percent_stations_available_analysis.py` | `results/cleaned_data/` |
   | 2. Compute daily percent of stations available | `pixi run analysis` | `analysis/percent_stations_available_analysis.py` | `results/percentages_by_day/` |
   | 3. Create plots | `pixi run plots` | `plot_creation/percent_stations_available_plots.R` | `results/plots/` |