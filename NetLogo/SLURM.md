# Running via Slurm

This document details how to run a classroom experiment via Slurm, e.g. on a supercomputer. This document focusses on running the jobs on the [Hamilton supercomputer](https://www.dur.ac.uk/arc/hamilton/); if you wish to run the Slurm scripts elsewhere please consult the relevant documentation for the supercomputer and check the Slurm parameters in the scripts.

## Before you start

Please read the [Hamilton documentation](https://www.dur.ac.uk/arc/hamilton/) to ensure you understand the basics about registering, logging in, file storage, and running jobs. (You probably do not need to know the details about types of job script in order to use the scripts provided here.)

Follow the instructions to register for an account.

## Copying NetLogo files to Hamilton

Ask @alisonrclarke for the link to the NetLogo file including extensions, then copy it to your home directory on Hamilton (either using the command below, or following the [storage instructions](https://www.dur.ac.uk/arc/hamilton/usage/storage/).

```bash
scp NetLogo.tgz <user>@hamilton.dur.ac.uk:.
```

Log on to Hamilton and extract the file into your home directory:

```bash
ssh <user>@hamilton.dur.ac.uk
tar xzf NetLogo.tgz
```

## Checking out the code

After ssh-ing to Hamilton, run:

```bash
git clone https://github.com/DurhamARC/classroom-abm.git
```

## Editing the experiment file

Edit one of the files in the `experiment-files` directory to make the changes you want in the experiment:

  * `experiment-sample.xml` runs on the sample of 10 classes in `../classes_input/ABM ten classes size adjusted.csv`; each run takes only a few minutes, so you can use this to try our many parameter variations at once to narrow down the ranges of parameters to change and values.
  * `experiment.xml` runs the entire data set; each run takes several hours, so it is recommended to run fewer than 24 runs at once (1 per core on a Hamilton 7 node).

For details of the XML format of experiment files, see the [NetLogo BehaviorSpace Guide](https://ccl.northwestern.edu/netlogo/docs/behaviorspace.html). If you are not sure how to alter the parameters, try making the change in the GUI then search the .nlogo file for `<experiments>` to see the effect of our changes, and copy the change to the relevant file.

## Running the experiment
After ssh-ing to Hamilton, run one of the following `sbatch` commands (replacing `<your-email-address>` with your email address):

```bash
cd classroom-abm
# EITHER:
#    To run on the smaller sample (experiment-sample.xml):
sbatch --mail-user=<your-email-address> run_experiment_sample.sh
# OR:
#    To run on the full data set (experiment.xml):
sbatch --mail-user=<your-email-address> run_experiment.sh
```

You should get an output like:

```
Submitted batch job 3259639
```

The job will then be added to the queue on Hamilton. To check its status, run:

```bash
sacct -j 3259639
```

which should give you some output like:

```
       JobID    JobName  Partition    Account  AllocCPUS      State ExitCode
------------ ---------- ---------- ---------- ---------- ---------- --------
3259347      run_exper+     par6.q   hamilton          1    PENDING      0:0
```

The state will change as the job runs, and you should receive emails when the job starts and ends.

## Retrieving the Output

Once the job has ended, you will want to retrieve the output from the `classes_output` directory inside `classroom-abm`. See the [storage instructions](https://www.dur.ac.uk/arc/hamilton/usage/storage/) for the best way to do this for your platform; it would speed things up to zip up its contents first:

```bash
cd ~
zip classes_output.zip classroom-abm/classes_output
```

`classes_output` contains many CSV files:

 * 1 file created by BehaviorSpace, with a filename like `experiment2020-12-01_142006.csv`, containing a row per run which shows the parameters tested and the summary outputs (mean, SD, correlations)
 * 1 file for each run with a name like `output2020-12-01_142435-10.csv` which gives the output values for each student in that run; the number at the end of the filename corresponds to the run number in the experiment CSV.

Note that the dates in the filenames are the date when the file was created; if you try running multiple experiments at once then you may not be able to tell which output file is from which experiment.
