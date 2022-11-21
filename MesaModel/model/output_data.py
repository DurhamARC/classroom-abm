import logging
import os

import pandas as pd
from multiprocessing import Lock

logger = logging.getLogger(__name__)

mutex = Lock()


class OutputDataWriter:
    def __init__(self, output_filepath):
        self.output_filepath = output_filepath
        self.columns = [
            "start_maths",
            "student_id",
            "class_id",
            "school_id",
            "N_in_class",
            "Ability",
            "Inattentiveness",
            "hyper_impulsive",
            "Deprivation",
            "end_maths",
        ]
        logger.debug("Finished init, output_filepath: %s", self.output_filepath)

    def write_data(self, agent_df, class_id, school_id, class_size):
        # Add class id and size into each row of data frame
        agent_df["class_id"] = class_id
        agent_df["school_id"] = school_id
        agent_df["N_in_class"] = class_size

        # Reorder columns to match our data
        agent_df = agent_df[self.columns]

        # Mutex is for parallel batchrunner
        logger.debug("Getting mutex")
        with mutex:
            logger.debug("Got mutex")
            if not os.path.exists(self.output_filepath):
                logger.debug("Creating new file")
                agent_df.to_csv(self.output_filepath, index=False, mode="a")
            else:
                logger.debug("Appending to existing file")
                agent_df.to_csv(
                    self.output_filepath, index=False, mode="a", header=False
                )

    # def add_missing_column(self, agent_df, school_id, columns):
    #     # Add missing columns in the input file and use the updated input file
    #     if school_id == 0:
    #         for column in columns:
    #             if column == 'school_id':
    #                 agent_df["school_id"] = 0
