# Agent-based modelling of a classroom

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Overview](#overview)
- [Running the Mesa model](#running-the-mesa-model)
	- [Contributing to the mesa model:](#contributing-to-the-mesa-model)
- [Multilevel analysis](#multilevel-analysis)
	- [Installation](#installation)
	- [Running the multilevel analysis](#running-the-multilevel-analysis)
	- [Running the full pipeline](#running-the-full-pipeline)
	- [Running the multilevel analysis on the Hamilton supercomputer](#running-the-multilevel-analysis-on-the-hamilton-supercomputer)

<!-- /TOC -->

## Overview
This repository uses Agent Based Modelling to model how much students learn according to how good the teacher is at classroom control and teaching.

The first iteration of this project was written in [NetLogo](https://ccl.northwestern.edu/netlogo/index.shtml) and was based on work by Peter Tymms. This is now stored in /NetLogo directory.

We are now developing another model using Mesa (see /MesaModel) and gratefully acknowledge Khulood Alharbi's [model](https://github.com/kuloody/ABM) which was used as a starting point for this work.

## Running the Mesa model

Install the dependencies and activate the Conda environment:

```
conda create --name classroom_abm --file conda_locks/conda-<operating-sys>-64.lock
conda activate classroom_abm
```

Execute python code on command line:

```
cd MesaModel
python run.py
```

More options for running the model:

```
Usage: run.py [OPTIONS]

Options:
  -i, --input-file TEXT         Input file path, relative to current working
                                directory

  -o, --output-file TEXT        Output file path, relative to current working
                                directory

  -p, --n-processors INTEGER  Number of processors to be used by the
                                batchrunner (used only if -a is set)

  -c, --class_id INTEGER        ID of class to run model for
  -a, --all_classes             Whether to run over all classes (overrides
                                class_id; not available in webserver mode)

  -w, --webserver               Whether to run an interactive web server
  --help                        Show this message and exit.
```

To run the model with the full pipeline (inlcuding multilevel analysis) see [below](###Running-the-full-pipeline).

### Contributing to the mesa model:

To use Black as a Git hook on all commits run `pre-commit install` from the root of the repository.

Add new dependencies to environment.yml. Then execute `conda-lock` from the root of the repository. This will create lock files for osx, linux and windows which we store in the conda_locks/ directory to minimise clutter:

```
conda-lock --filename-template conda_locks/conda-{platform}.lock
```

To add new dependencies from an updated lock file rerun:

```
conda create --name classroom_abm --file conda_locks/conda-<operating-sys>-64.lock
```

## Multilevel analysis

The multilevel_analysis folder contains scripts to run a multilevel model over the data, and calculate a mean square error score. It uses [MLwiN](http://www.bristol.ac.uk/cmm/software/mlwin/) via its R script, R2MLWin.

The R directory contains:

 * A `classroommlm` directory containing an R package with 2 methods, `null_model` and `full_model`, which runs the multilevel model over the given data, and produces the coefficients and variances.
 * A `run_mlm` R project (using `renv` for package management) which imports the CSV `classes_input/test_input.csv` and runs the models from `classroommlm`.

The `multilevel_analysis.py` script runs the multilevel model from R, and calculates the mean squared error. The `run_pipeline.py` script runs the agent based model, then calculautes the mean squared error.

### Installation

  1. Set up and activate a conda environment as above.
  2. Install R (e.g. `brew install R`)
  3. Install MLwiN and mlnscript, for which you will need a license:
    1. Sign up for an academic account at https://www.cmm.bristol.ac.uk/clients/reqform/
    2. Download `mlnscript` for MacOS/linux by filling in form at https://www.cmm.bristol.ac.uk/clients/softwaredownload/
    3. Run the installer (.dmg, .rpm, etc). If prompted for a directory, save the files to a folder such as `/opt/mln`.
    4. If the installer extracts the files to a path other than `/opt/mln`, set an environment variable `MLNSCRIPT_PATH` to where the file `mlnscript` has been saved.
  4. Build the build the `classroommlm` R package and copy the output to the `renv` local packages dir:

  ```bash
  cd multilevel_analysis/R
  R CMD build classroommlm
  cp classroommlm*.tar.gz run_mlm/renv/local
  ```

  (You'll need to do this whenever changes are made in the `classroommlm` directory.)

### Running the multilevel analysis
Run the script from the `multilevel_analysis` directory:

```bash
cd multilevel_analysis
python multilevel_analysis.py
```

Options for running the script:

```bash
Usage: multilevel_analysis.py [OPTIONS]

Options:
  -r, --real-data-file TEXT       File path containing real data, relative to
                                  multilevel_analysis directory. Defaults to
                                  ../classes_input/test_input.csv
  -s, --simulated-data-file TEXT  Output file path, relative to current
                                  working directory  [required]
  --help                          Show this message and exit.
```

### Running the full pipeline
You can run the model and calculate the mean squared error using the `run_pipeline.py` script
from the `multilevel_analysis` directory:

```bash
cd multilevel_analysis
python run_pipeline.py -i ../classes_input/test_input_short.csv
```

`run_pipeline.py` accepts input and output file parameters:

```bash
Usage: run_pipeline.py [OPTIONS]

Options:
  -i, --input-file TEXT         File path containing real data, relative to
                                multilevel_analysis directory. Defaults to
                                ../classes_input/test_input.csv

  -o, --output-file TEXT        Output file path, relative to current working
                                directory.

  -p, --n-processors INTEGER  Number of processors to be used by the
                                batchrunner

  --help                        Show this message and exit.
```

### Running the multilevel analysis on the Hamilton supercomputer

Issue the following commands:

```
module purge
module load miniconda2/4.1.11
module load r/4.0.3
```

Activating the conda environment is slightly different:

```
source activate classroom_abm
```

Then download MLwiN and mlnscript as described above, but be sure to download it for Centos 7. Use scp and put it in /ddn/data/<usr>. Then issue the following commands:

```
rpm2cpio mlnscript-3.05-1.el7.x86_64.rpm | cpio -idv
export MLNSCRIPT_PATH=/ddn/data/$USER/usr/bin/mlnscript
export LD_LIBRARY_PATH=/ddn/data/$USER/usr/lib64
```

Then build the classroommlm R package and run as described above.
