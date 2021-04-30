# Agent-based modelling of a classroom

This repository uses Agent Based Modelling to model how much students learn according to how good the teacher is at classroom control and teaching.

The first iteration of this project was written in [NetLogo](https://ccl.northwestern.edu/netlogo/index.shtml) and was based on work by Peter Tymms. This is now stored in /NetLogo directory.

We are now developing another model using Mesa (see /MesaModel) and gratefully acknowledge Khulood Alharbi's [model](https://github.com/kuloody/ABM) which was used as a starting point for this work.

## Running the Mesa model

Install the dependencies and activate the Conda environment:

```
conda create --name classroom_abm --file conda_locks/conda-<operating-sys>-64.lock
conda activate classroom_abm
```

Execute python code:

```
cd MesaModel
python server.py run.py
```

### Contributing to the mesa model:

To use Black as a Git hook on all commits run `pre-commit install` from the root of the repository.

Add new dependencies to environment.yml. Then execute `conda-lock` from the root of the repository. This will create lock files for osx, linux and windows which we store in the conda\_locks/ directory to minimise clutter:

```
conda-lock --filename-template conda_locks/conda-{platform}.lock
```

To add new dependencies from an updated lock file rerun:

```
conda create --name classroom_abm --file conda_locks/conda-<operating-sys>-64.lock
```

## Multilevel analysis

The multilevel_analysis folder contains scripts to run a multilevel model over the data. It uses [MLwiN](http://www.bristol.ac.uk/cmm/software/mlwin/) via its R script, R2MLWin.

The R directory contains:

 * A `classroommlm` directory containing an R package with 2 methods, `null_model` and `full_model`, which runs the multilevel model over the given data, and produces the coefficients and variances.
 * A `run_mlm` R project (using `renv` for package management) which imports the CSV `classes_input/test_input.csv` and runs the models from `classroommlm`.

The `multilevel_analysis.py` script runs the model from R (currently just to show it can be used from python).

### Installation

  1. Set up and activate a conda environment as above.
  2. Install R (e.g. `brew install R`)
  4. Install MLwiN and mlnscript, for which you will need a license:
    1. Sign up for an academic account at https://www.cmm.bristol.ac.uk/clients/reqform/
    2. Download `mlnscript` for MacOS/linux by filling in form at https://www.cmm.bristol.ac.uk/clients/softwaredownload/
    3. Run the installer (.dmg, .rpm, etc). If prompted for a directory, save the files to a folder such as `/opt/mln`.
    4. If the installer extracts the files to a path other than `/opt/mln`, set an environment variable `MLNSCRIPT_PATH` to where the file `mlnscript` has been saved.

### Running

Run the script from the `multilevel_analysis` directory:

```bash
cd multilevel_analysis
python multilevel_analysis.py
```
