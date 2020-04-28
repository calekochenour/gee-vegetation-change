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

Follow these steps upon completion of the *Binder Setup Instructions* or *Local Setup Instructions* to run the analysis in Jupyter Notebook:

Navigate to the `01-code-scripts` folder.

Click on `gee-vegetation-change-methods-columbia.ipynb` file to open in.

In cell 9 (code cell 3), change the `gee_username` to your GEE user name and change `gee_asset_folder` to an existing folder in your GEE Assets. The user name and folder will be used as the export destination for the results.

From the top of the page, select the `Kernal` tab and then the `Restart & Run All` option.

Select the `Restart and Run All Cells` button in the pop-up window.

The Jupyter Notebook will halt at cell 7 (code cell 2) and require authentication to GEE.

Click the hyperlink that appears in cell 7 (code cell 2), choose a GEE account/email to authenticate with, and select the `Allow` button to allow the Google Earth Engine Python Authenticator to access to your Google Account.

Copy the authentication code from the browser, return to the Jupyter Notebook tab, and paste the code into the `Enter verification code` field that appears in cell 7 (code cell 2).

Press return/enter, and the workflow will continue (remainder of the cells will run) if the authentication succeeds.

## Contents

The project contains folders for all stages of the workflow as well as other files necessary to run the analysis.

### `01-code-scripts/`

Contains all Python scripts and Jupyter Notebooks required to run the analysis.

### `environment.yml`

Contains the information required to create the Conda environment.
