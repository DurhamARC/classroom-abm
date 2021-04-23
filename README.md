# Agent-based modelling of a classroom

This repository uses Agent Based Modelling to model how much students learn according to how good the teacher is at classroom control and teaching.

The first iteration of this project was written in [NetLogo](https://ccl.northwestern.edu/netlogo/index.shtml) and was based on work by Peter Tymms. This is now stored in /NetLogo directory.

We are now developing another model using Mesa (see /Mesa) and gratefully acknowledge Khulood Alharbi's [model](https://github.com/kuloody/ABM) which was used as a starting point for this work.

## Running the Mesa model

Install the dependencies and activate the Conda environment:

```
conda create --name classroom_abm --file conda_locks/conda-<operating-sys>-64.lock
conda activate classroom_abm
```

Execute python code:

```
python3 model.py
python3 server.py
python3 run.py
```

### Contributing to the mesa model:

To use Black as a Git hook on all commits run `pre-commit install` from the root of the repository.

Add new depencies to environment.yml. Then execute `conda-lock` from the root of the repository. This will create lock files for osx, linux and windows which we store in the conda\_locks/ directory to minimise clutter:

```
conda-lock --filename-template conda_locks/conda-{platform}.lock
```

To add new dependencies from an updated lock file rerun:

```
conda create --name classroom_abm --file conda_locks/conda-<operating-sys>-64.lock
```

## Multilevel analysis

The multilevel_analysis folder contains scripts to run a multilevel model over the data. It uses [MLwiN](http://www.bristol.ac.uk/cmm/software/mlwin/) via its R script, R2MLWin.

The `classroommlm` directory contains an R package with 2 methods, `null_model` and `full_model`, which run the multilevel
model over the given data, and produce the coefficients and variances.

The `multilevel_analysis.py` script imports the CSV `classes_input/test_input.csv` to a pandas dataframe, then uses
`rpy2` to run the models from `classroommlm`.

### Installation

  1. Set up and activate a conda environment as above.
  2. Install rpy2 via pip (as we can't install all the necessary R packages from conda's `r-base` package):
     ```bash
     conda install pip
     pip install rpy2
     ```
  3. Install R (e.g. `brew install R`)
  4. Install MLwiN and mlnscript, for which you will need a license:
    1. Sign up for an academic account at https://www.cmm.bristol.ac.uk/clients/reqform/
    2. Download `mlnscript` for MacOS/linux by filling in form at https://www.cmm.bristol.ac.uk/clients/softwaredownload/
    3. Open the installer (.dmg, .rpm, etc) and save the files to a folder such as `/opt/mln`. (This is the path you will need to pass to the `null_model` and `full_model` functions in `classroommlm` or `multilevel_analysis.py`.)

### Running

Run the script from the `multilevel_analysis` directory, passing the path to `mlnscript` if it is anything other than
`/opt/mln/mlnscript`:

```bash
cd multilevel_analysis
python multilevel_analysis.py <optional_path_to_mlnscript>
```
