# Agent-based modelling of a classroom

This repository uses Agent Based Modelling to model how much students learn according to how good the teacher is at classroom control and teaching.

The first iteration of this project was written in [NetLogo](https://ccl.northwestern.edu/netlogo/index.shtml) and was based on work by Peter Tymms. This is now stored in /NetLogo directory.

We are now developing another model using Mesa (see /Mesa) and gratefully acknowledge Khulood Alharbi's [model](https://github.com/kuloody/ABM) which was used as a starting point for this work.

To use Black as a Git hook on all commits run `pre-commit install` from the root of the repository. To install dependencies load the conda lock file as follows: `conda create --name fromlock --file conda_locks/conda-<operating-sys>-64.lock`
