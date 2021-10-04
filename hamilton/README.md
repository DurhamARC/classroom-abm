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
			- [merge_repeats.py](#mergerepeatspy)
			- [plot_correlations.py](#plotcorrelationspy)
			- [merge_best_results.py](#mergebestresultspy)
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

```
module purge
module load miniconda2/4.1.11
conda create --name classroom_abm --file conda_locks/conda-linux-64.lock
```

To activate the conda environment, use:

```
source activate classroom_abm
```


### Multilevel analysis

Issue the following commands:

```
module load r/4.0.3
```

Download MLwiN and mlnscript as described in the main [README](https://github.com/DurhamARC/classroom-abm/blob/master/README.md), but be sure to download it for Centos 7. Use scp from your own machine to put the file in `/ddn/data/<usr>`. Then issue the following commands:

```
cd /ddn/data/$USER
rpm2cpio mlnscript-3.05-1.el7.x86_64.rpm | cpio -idv
export MLNSCRIPT_PATH=/ddn/data/$USER/usr/bin/mlnscript
export LD_LIBRARY_PATH=/ddn/data/$USER/usr/lib64
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
module load python/3.6.8
```

Then clone and install ReFrame:

```
git clone https://github.com/eth-cscs/reframe.git
cd reframe
./bootstrap.sh
./bin/reframe -V
```

## Single runs

There is an example job script in this directory that illustrates how the MesaModel can be run on Hamilton:
`example_slurm_scripts/batchrunner_with_six_classes.sh`.

This runs all 6 classes in `../classes_input/test_input_short.csv` but will not run
the full pipeline (for that use the above structure
on `../multilevel_analysis/run_pipeline.py`). To run on
the full dataset add `-i` `../classes_input/test_input.csv`
If you do this set `-p` to 24 to exploit all of the cores
one of Hamilton's par7.q nodes.

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

Navigate to the test directory, open a screen session and run:

```
cd ~/classroom-abm/hamilton/reframe_parameterisation_infrastructure/reframe_tests
screen
./parameterisation.sh --with-<small/big>-dataset
```

This assumes that the classroom-abm repo is setup with a working multilevel model implementation.
The steps for how to do this on Hamilton are documented above. Further,
at the moment this will just run the pipeline with three different numbers of processors
(8, 16 and 24). Once our parameter set is stable they will all be added following Latin Hypercube sampling.

Tests will run independently over as many nodes as SLURM allows adding an extra layer of
'parallelism' to what was achieved with Mesa's BatchRunnerMP.

By default, ReFrame only runs one repeat of each parameter set. To change this export the following
environment variable prior to calling ReFrame:

```
export NUM_REPEATS=<n>
```

Note: Hamilton accepts a maximum of 50 jobs from a single user at any time. So if 2 repeats are run for
30 parameter sets, 10 will automatically fail.


### Quick setup

The script `setup_new_run.sh` in the `hamilton` directory will generate and display the parameter files, and show you the commands to run to set off reframe.

```
./hamilton/setup_new_run.sh
```

### Postprocessing

We currently have various postprocessing scripts that allow users to get results
from Hamilton and do some sorting and very basic analysis.

#### fetch_files.sh

`fetch_files.sh` copies the output files from Hamilton into the `parameter_analysis` directory and runs
`merge_repeats.py` and `plot_correlations.py` on them.

To run (from its own directory):

```
DATE_TO_FETCH=2021-09-13 TIME_TO_FETCH=141114 ./fetch_files.sh
```

Note that you only need to set `DATE_TO_FETCH` to fetch a previous day's results, and `TIME_TO_FETCH` if you have done multiple
runs in one day (to avoid fetching multiple results from `/ddn/home/$USER/classroom-abm/hamilton/mse_results_from_reframe`).
If set, `TIME_TO_FETCH` should match the time in the filenames inside that folder on Hamilton, e.g. if the file is `/ddn/home/$USER/classroom-abm/hamilton/mse_results_from_reframe/mse_output_2021-09-07_144734.zip` then use `TIME_TO_FETCH=144734`.

**NB `fetch_files.sh` assumes only a single reframe run rather than multiple parts.**

#### merge_repeats.py

`merge_repeats.py` merges the MSE csvs produced
by ReFrame's postrun command. Each time we trigger a ReFrame run over all our parameter sets we get
one csv that maps parameter sets to MSEs so we offer the functionality to merge them and sort them in
`mse_results_from_reframe/merge_repeats.py`. The outputs will be called `lowest_to_highest_mses.csv` and
`merged_mses.csv` repectively and can be called on an arbitrary number of input csvs as follows:

```
python merge_repeats.py <csv1> <csv2> <csvN>
```

Additional scripts have been added to the `parameter_analysis` directory. These assume that the shared
folder containing parameterisation results has been symlinked to the classroom_abm directory.

#### plot_correlations.py

`plot_correlations.py` runs a basic script over the results which creates scatter plots of each parameter
against the mean squared error. It accepts a directory and CSV filename as parameters, and outputs a file
`correlations.png` in the directory.

e.g.

```
python plot_correlations.py ../../parameterisation_results best_mses.csv
```

#### merge_best_results.py

`merge_best_results.py` gets the best results from the `parameter_analysis` folder and creates a CSV `best_mses.csv`
containing all the parameter sets which gave MSE scores < 3.5.

To run (from its own directory):

```
python merge_best_results.py ../../parameterisation_results
```

### Hamilton issues

Hamilton login nodes automatically kill your processes when you log out, even if they are nohup'd. This is
something that will be changed for Hamilton 8. It is problematic when using ReFrame because at
a high level ReFrame's work flow is as follows:

 1) Setup a test
 2) Issue jobs to SLURM
 3) Wait until SLURM jobs complete
 4) Evaluate Sanity checks, perform postrun commands etc.

Step (4) is important for us, we use it to collate results and check tests have executed
successfully. It can only take place if the ReFrame process is not cancelled during step 3.
Further, terminating ReFrame during step 3 has the consequence of cancelling the SLURM jobs that
are submitted under that  process. Given that our runs are long we need a strategy to ensure the
ReFrame process is not killed during our runs, else we would have to ensure our live terminal
session is sustained throughout the duration of our runs (impractical).

The easiest solution to the problem of having an always open connection to hamilton is to use
the NCC cluster in Comp Sci. We run a tmux session on NCC's headnode, and in there have an
ssh session to hamilton. We have the following workflow:

Access NCC through ssh (use Durham's VPN), begin a tmux session called abm-session
and tunnel into Hamilton:

```
ssh <user>@ncc1.clients.dur.ac.uk
tmux new -s abm-session
ssh <user>@hamilton.dur.ac.uk
```

Start ReFrame as described above and operate the tmux session with the following commands:

```
Ctrl-b + [									to scroll
ctrl-b + d									to detach
tmux attach-session -t abm-session   		to reattach
```

To kill the session once done:
```
tmux kill-session -t 0
```
