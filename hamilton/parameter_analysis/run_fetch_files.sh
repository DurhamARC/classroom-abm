#!/usr/bin/env bash

# A script for convenience to run on the local machine.
# It sets necessary env variables and fetches result files from remote to local.
# The env variables to set by user are:
#   USER .. your user name on the remote machine if it's different from the local one
#      (in our case, on `hamilton` supercomputer)
#   REFRAME_TEST .. the name of the parametrisation test you've just run
#      (this constitutes a part of the directory name where output results on the remote machine have been saved)
#   DATE_TO_FETCH .. the date of the simulation
#      (in the simplest case of the simulation which ran only on this particular date)
#   [optional] LOCAL_RESULTS_DIR .. the directory name where to store the results
#      (Dmitry's note: in my case, I introduced this variable to store the results on a different partition with larger data storage size)

export USER=lcgk69 # comment out this line if the usernames coincide with each other locally and remotely
export REFRAME_TEST="variation-with-feedback"
export DATE_TO_FETCH=2022-08-01
export LOCAL_RESULTS_DIR="$HOME/Work/classroom-abm/parameterisation_results"

# Don't modify after this line
export REMOTE_RESULTS_DIR="classroom_abm_${REFRAME_TEST}"

./fetch_files.sh
