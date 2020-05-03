# Google Earth Engine (GEE) Vegetation Change

This directory contains the code to produce a vegetation change analysis of a study area in the Tolima Department, Columbia. The workflow computes the NDVI difference between peak green and post-harvest imagery and classifies change based on NDVI thresholds.

## Prerequisites

To run this analysis locally or online with Binder, you will need:

 * [Google Earth Engine](https://earthengine.google.com/) account

If running this locally, you will also need:

 * Conda ([Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://docs.anaconda.com/anaconda/install/))

## Binder Setup Instructions
To run this analysis in a web browser, click the icon below to launch the project with Binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/calekochenour/gee-vegetation-change/master)

## Local Setup Instructions

To run this analysis from a terminal, navigate to the folder containing the local repository.

Local instructions assume the user has cloned or forked the GitHub repository.

### Create and Activate Conda Environment

From the terminal, you can create and activate the project Conda environment.

Create environment:

```bash
conda env create -f environment.yml
```

Activate environment:

```bash
conda activate gee-vegetation-change
```

### Open Jupyter Notebook

From the terminal, you can run the analysis and produce the project outputs.

Open Jupyter Notebook:

```bash
jupyter notebook
```

## Run the Analysis

Follow these steps upon completion of the **Binder Setup Instructions** or **Local Setup Instructions** to run the analysis in Jupyter Notebook:

* Navigate to the `01-code-scripts` folder;

* Click on the `gee-vegetation-change-methods-columbia.ipynb` file;

* Change the `gee_username` variable to a valid GEE user name and change `gee_asset_folder` to an existing folder in the account's GEE Assets (Cell 9, Code Cell 3);

* Select the `Kernal` tab and then the `Restart & Run All` option from the top of the browser page;

* Select the `Restart and Run All Cells` button in the pop-up window;

* Click the hyperlink that appears (Cell 7, Code Cell 2), choose a GEE account/email to authenticate with, and select the `Allow` button to allow the Google Earth Engine Python Authenticator to access the GEE Account;

* Copy the authentication code that appears in the browser, return to the Jupyter Notebook tab, and paste the authentication code into the `Enter verification code` field that appears (Cell 7, Code Cell 2); and,

* Press `return`/`enter` to authenticate and run the remainder of the Jupyter Notebook cells.

If the user specified an existing GEE Assets folder and succesfully authenticated to GEE, the workflow will run all code and display the results of the analysis in an interactive map.

## Contents

The project contains folders for all stages of the workflow as well as other files necessary to run the analysis.

### `01-code-scripts/`

Contains all Python scripts and Jupyter Notebooks required to run the analysis.

### `environment.yml`

Contains the information required to create the Conda environment.
