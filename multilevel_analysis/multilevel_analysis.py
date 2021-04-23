import os
import sys

import pandas as pd

import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

utils = rpackages.importr("utils")

# Install R2MLWiN - TODO: see if we can cache this
utils.chooseCRANmirror(ind=1)
utils.install_packages("R2MLwiN")
utils.install_packages("classroommlm_0.1.0.tar.gz", type="source")

base = rpackages.importr("base")
classroom_mlm = rpackages.importr("classroommlm")

if len(sys.argv) > 1:
    mlnscript_path = sys.argv[1]
else:
    mlnscript_path = "/opt/mln/mlnscript"

# Import data from CSV to dataframe and clean
csv_filename = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "classes_input/test_input.csv",
)
pupil_df = pd.read_csv(csv_filename)
pupil_df.end_maths = pupil_df.end_maths.apply(pd.to_numeric, errors="coerce")
pupil_df = pupil_df.dropna()

# Convert to R data frame
with localconverter(ro.default_converter + pandas2ri.converter):
    r_pupil_df = ro.conversion.py2rpy(pupil_df)

# Null model
r_null_model = classroom_mlm.null_model(r_pupil_df, mlnscript_path)

with localconverter(ro.default_converter + pandas2ri.converter):
    null_model_df = ro.conversion.rpy2py(r_null_model)

print(null_model_df)

# Full model
r_full_model = classroom_mlm.full_model(r_pupil_df, mlnscript_path)

with localconverter(ro.default_converter + pandas2ri.converter):
    full_model_df = ro.conversion.rpy2py(r_full_model)

print(full_model_df)
