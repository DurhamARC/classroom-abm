# Running on Hamilton

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Running on Hamilton](#running-on-hamilton)
	- [Installation](#installation)
		- [Code checkout](#code-checkout)
		- [Set up the conda environment](#set-up-the-conda-environment)
		- [Multilevel analysis](#multilevel-analysis)
		- [Reframe](#reframe)
	- [Single runs](#single-runs)
	- [Parameterisation](#parameterisation)
		- [Generating parameters: Latin Hypercube Sampling](#generating-parameters-latin-hypercube-sampling)
		- [Deploying automated parameterisation tests via Reframe](#deploying-automated-parameterisation-tests-via-reframe)
		- [Quick setup](#quick-setup)
		- [Postprocessing](#postprocessing)
			- [fetch_files.sh](#fetchfilessh)
		- [cli.py](#clipy)
			- [merge-repeats](#merge-repeats)
			- [plot-correlations](#plot-correlations)
			- [merge-best-results](#merge-best-results)
			- [run-webserver-with-params](#run-webserver-with-params)
		- [Hamilton issues](#hamilton-issues)

<!-- /TOC -->

## Installation

### Code checkout

```
git clone https://github.com/DurhamARC/classroom-abm.git
```

If you are modifying parameters on a branch, check out the branch using:

```
git checkout <branch_name>
```

### Set up the conda environment

Currently conda is not available as a module on Hamilton8, so needs to be manually installed in your home directory:

```
cd $HOME
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod a+x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source .bashrc
```

(Accept the default installation directory, which should be your home directory.)

Then create the classroom_abm environment:

```
cd $HOME/classroom-abm
conda create --name classroom_abm --file conda_locks/conda-linux-64.lock
```

To activate the conda environment, use:

```
source activate classroom_abm
```


### Multilevel analysis

Issue the following commands:

```
module load r/4.1.2
module load $R_BUILD_MODULES
```

Download MLwiN and mlnscript as described in the main [README](https://github.com/DurhamARC/classroom-abm/blob/master/README.md), but be sure to download it for RedHat/Rocky. Use scp from your own machine to put the file in `$NOBACKUP`. Then issue the following commands:

```
cd $NOBACKUP
rpm2cpio mlnscript-3.05-1.el7.x86_64.rpm | cpio -idv
export MLNSCRIPT_PATH=$NOBACKUP/usr/bin/mlnscript
export LD_LIBRARY_PATH=$NOBACKUP/usr/lib64:$LD_LIBRARY_PATH
ln -s /apps/developers/libraries/openblas/0.3.18/1/gcc-11.2/lib/libopenblas.so /nobackup/ksvf48/usr/lib64/libblas.so.3
ln -s /apps/developers/libraries/openblas/0.3.18/1/gcc-11.2/lib/libopenblas.so /nobackup/ksvf48/usr/lib64/liblapack.so.3
```

Then build the classroommlm R package and run as described [here](https://github.com/DurhamARC/classroom-abm/blob/master/README.md)

### Reframe

We use [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/index.html)
to automate our parameterisation pipeline. The workflow assumes the following
steps have been taken. To setup ReFrame enter your home directory and
load python:

```
cd ~/
module purge
module load python/3.9.9
```

Then clone and install ReFrame:

```
git clone https://github.com/eth-cscs/reframe.git
cd reframe
./bootstrap.sh
./bin/reframe -V
```

## Single runs

There are some example job scripts in the `example_slurm_scripts` directory that illustrate how the MesaModel can be
run on Hamilton8:

 * `batchrunner_with_two_classes.sh` runs the Mesa model over 2 classes in `../classes_input/test_input_2_classes.csv` (but does not run the multilevel analysis)
 * `batchrunner_with_six_classes.sh` runs the Mesa model on the 6 classes in `../classes_input/test_input_short.csv`
 * `batchrunner_pipeline_two_classes.sh` runs the full pipeline (including multilevel modelling) on 2 classes in `../classes_input/test_input_2_classes.csv`
 * `batchrunner_pipeline_six_classes.sh` runs the full pipeline on the classes in `../classes_input/test_input_short.csv`

## Parameterisation

See [Quick Setup](#quick-setup) for a quick way to set off a new run.

### Generating parameters: Latin Hypercube Sampling

If one does not want to generate parameters by Latin Hypercube Sampling (LHS) then skip this step.
The file `hamilton/parameter_input/lhs_sampling.csv` will be used by default which contains four
sets of parameter examples that will fuel four ReFrame test cases.

Better, is to use LHS sampling to generate a parameter csv that can then be passed to ReFrame.
We offer the facility to calculate parameters using maximum-minimum distance LHS. ReFrame
will then work through these parameter sets in turn.

To run this, do:

```
cd hamilton/parameter_input
python lhs_sampling.py
```

This will generate 30 sets of parameters in a new file: `lhs_params.csv`. To use this with ReFrame simply
execute:

```
export PARAMETER_FILE=<path-to-parameter-file>
```

Note: the call to `lhs_sampling.py` can be configured with the following options:

```
  -ns, --num-param-sets INTEGER  How many sets of params to generate (this
                                 will equal the number of ReFrame tests)
  -o, --output-file TEXT         Output file path, relative to current working
                                 directory
  --help                         Show this message and exit.
```

The sampling algorithm is fixed with a random seed so if you rerun the tool you will get the same
output provided `-ns` is set to the same value.

If you want to write your own parameter file then you can do so - remember to set `PARAMETER_FILE` accordingly
prior to running ReFrame.

### Deploying automated parameterisation tests via Reframe

Ensure that the classroom-abm repo is set up with a working multilevel model implementation, as documented above.

Navigate to the test directory, open a [screen](https://linuxize.com/post/how-to-use-linux-screen/) session and run the tests as follows:

```bash
cd ~/classroom-abm/hamilton/reframe_parameterisation_infrastructure/reframe_tests
screen -S classroom_abm_parameterisation
export HAMILTON_VERSION=hamilton8
export PARAMETER_FILE=<path-to-param-csv>
export NUM_ITERATIONS=<num_iterations>
export NUM_REPEATS=<num_repeats>
./parameterisation.sh --with-<small/medium/big>-dataset
```

where:

 * `$PARAMETER_FILE` is the CSV to use as a starting point (e.g. generated via `lhs_sampling.py` or `python cli.py generate-next-params ...`)
 * `$NUM_REPEATS` is the number of times to repeat each step (defaults to 1)
 * `$NUM_ITERATIONS` is the number of iterations of parameter sets to run (defaults to 1). This runs a fairly naive algorithm which uses the best result from the previous run to set ranges for Latin Hypercube Sampling, generating a new CSV of parameters and setting off another set of jobs via reframe. The range around the mean decreases with each iteration (see `automation.py` in `parameter_analysis`).

Tests will run independently over as many nodes as SLURM allows adding an extra layer of
'parallelism' to what was achieved with Mesa's BatchRunnerMP.

Note: Hamilton accepts a maximum of 50 jobs from a single user at any time. So if 2 repeats are run for
30 parameter sets, 10 will automatically fail.

Using `screen` should mean that if you disconnect from Hamilton whilst Reframe is running, you should be able to reconnect
to the session when you log back in:

```bash
screen -r classroom_abm_parameterisation
```

(or just use `screen -r` if you don't have any other `screen` sessions open).

Use of screen is necessary using ReFrame because at a high level ReFrame's work flow is as follows:

 1) Setup a test
 2) Issue jobs to SLURM
 3) Wait until SLURM jobs complete
 4) Evaluate Sanity checks, perform postrun commands etc.

Step (4) is important for us, we use it to collate results and check tests have executed
successfully. It can only take place if the ReFrame process is not cancelled during step 3.
Further, terminating ReFrame during step 3 has the consequence of cancelling the SLURM jobs that
are submitted under that  process. Given that our runs are long we need a strategy to ensure the
ReFrame process is not killed during our runs; using `screen` ensures the ReFrame process continues
to run even if we log out of hamilton.


### Quick setup

The script `setup_new_run.sh` in the `hamilton` directory will generate and display the parameter files, and show you the commands to run to set off reframe.

```
./hamilton/setup_new_run.sh
```

### Postprocessing

We currently have various postprocessing scripts in `hamilton/parameter_analysis` that allow users to get results
from Hamilton and do some sorting and very basic analysis. These assume that the shared
folder containing parameterisation results has been symlinked to the classroom_abm directory (or a folder called
`parameterisation_results`) has been created.

### fetch_files.sh

`fetch_files.sh` copies the output files from Hamilton into the `parameterisation_results` directory and runs
`merge_repeats` and `plot_correlations` on them (see below).

To run (from its own directory):

```
DATE_TO_FETCH=2021-09-13 TIME_TO_FETCH=141114 ./fetch_files.sh
```

Note that you only need to set `DATE_TO_FETCH` to fetch a previous day's results, and `TIME_TO_FETCH` if you have done multiple
runs in one day (to avoid fetching multiple results from `$HOME/classroom-abm/hamilton/mse_results_from_reframe`).
If set, `TIME_TO_FETCH` should match the time in the filenames inside that folder on Hamilton, e.g. if the file is `$HOME/classroom-abm/hamilton/mse_results_from_reframe/mse_output_2021-09-07_144734.zip` then use `TIME_TO_FETCH=144734`.

You can also use `START_TIME` and `END_TIME` to specify a range of result folders within a day, or `START_DAY` and
`END_DAY` to specify a range of dates within the same month, e.g. `START_DAY=25 END_DAY=26`. (NB: the way this works is
slightly naive so it won't work across month boundaries or if you try to use both start/end day and time at the same
time! If not all data is fetched as expected, use separate commands to fetch the data then manually move the folders and
run the CLI commands below to merge repeats and plot correlations.)

### cli.py

`cli.py` in `hamilton/parameter_analysis` provides various utility tools. To see the full list, run:


```bash
python cli.py --help
```

The most common commands are documented below; others are used by scripts on Hamilton.

#### merge-repeats

`cli.py merge-repeats` merges the MSE csvs produced
by ReFrame's postrun command. Each time we trigger a ReFrame run over all our parameter sets we get
one csv that maps parameter sets to MSEs so we offer the functionality to merge them and sort them.
The outputs will be called `lowest_to_highest_mses.csv` and
`merged_mses.csv` repectively and can be called on an arbitrary number of input csvs as follows:

```
python cli.py merge-repeats <csv1> <csv2> <csvN>
```

#### plot-correlations

`cli.py plot-correlations` runs a basic script over the results which creates scatter plots of each parameter
against the mean squared error. It accepts a directory and CSV filename as parameters, and outputs a file
`correlations.png` in the directory.

e.g.

```
python cli.py plot-correlations -i ../../parameterisation_results/best_mses.csv
```

#### merge-best-results

`cli.py merge-best-results` gets the best results from a given folder and creates a CSV `best_mses.csv`
containing all the parameter sets which gave MSE scores lower than a particular limit (defaults to 3).

To run (from its own directory):

```
python cli.py merge-best-results -d ../../parameterisation_results
```

#### run-webserver-with-params

`cli.py run-webserver-with-params.py` runs the web version of the model with a set of params taken from a CSV.

e.g. to run the 1st row in the `lowest_to_highest_mses.csv` from the result on 2021-09-24:

```
python cli.py run-webserver-with-params -f ../../parameterisation_results/2021-09-24_part_001/lowest_to_highest_mses.csv -r 0
```
