# Google Earth Engine Vegetation Change

This directory contains the code to produce a vegetation change analysis of a study area in the Tolima Department, Columbia. The workflow computes the NDVI difference between peak green and post-harvest imagery and classifies change based on NDVI thresholds.

## Prerequisites

To run this project locally, you will need:

* Conda ([Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://docs.anaconda.com/anaconda/install/))

### Binder Instructions

To run this project in a web browser, click the icon below to launch the project with Binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/calekochenour/gee-vegetation-change/master)

Binder will open Jupyter Notebook in the current web browser. Click "New" and select "Terminal" to open a terminal in the project folder.

## Instructions

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

### Run the Analysis

From the terminal, you can run the analysis and produce the project outputs.

## Contents

The project contains folders for all stages of the workflow as well as other files necessary to run the analysis.

### `01-code-scripts/`

Contains all Python scripts and Jupyter Notebooks required to run the analysis.

### `environment.yml`

Contains the information required to create the Conda environment.
