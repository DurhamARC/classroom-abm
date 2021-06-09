# Running on Hamilton

### Single runs

There is an example job script in this directory that illustrates how the MesaModel can be run on Hamilton: 
`example_slurm_scripts/batchrunner_with_six_classes.sh`.

This runs all 6 classes in `../classes_input/test_input_short.csv` but will not run 
the full pipeline (for that use the above structure
on `../multilevel_analysis/run_pipeline.py`). To run on
the full dataset add `-i` `../classes_input/test_input.csv`
If you do this set `-p` to 24 to exploit all of the cores
one of Hamilton's par7.q nodes.

### Parameterisation

We use [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/index.html)
to automate our parameterisation pipeline. The workflow assumes the following
steps have been taken. To setup ReFrame enter your home directory (we assume ReFrame 
is in the home directory) and load python:

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

From there navigate to the test directory, open a screen session and run:

```
cd ../classroom-abm/MesaModel/hamilton/reframe_parameterisation_infrastructure/reframe_tests
screen
./parameterisation.sh --with-<small/big>-dataset
```

This assumes that the classroom-abm repo is setup with a working multilevel model implementation. 
The steps for how to do this on Hamilton are documented in the top level README. Further,
at the moment this will just run the pipeline with three different numbers of processors 
(8, 16 and 24). Once our parameter set is stable they will all be added following Latin Hypercube sampling.

Tests will run independently over as many nodes as SLURM allows adding an extra layer of 
'parallelism' to what was achieved with Mesa's BatchRunnerMP.