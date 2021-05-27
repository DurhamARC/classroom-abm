"""
This is a simple script that extracts the logic of the pupil step
in natural language. The logic is recorded in model/pupil.py in comments
that begin with the string '# If ' and describe the conditions under
which a pupil's learning state evolves over time. We extract these
comments in a file called pupil_logic.txt so that it can be shared with
and verfied by colleagues in the Education Department at Durham University.
"""

with open("model/Pupil.py", "r") as pupil_logic_input:
    with open("pupil_logic.txt", "w") as pupil_logic_output:
        comment_block = False
        for line in pupil_logic_input:

            if "# If " in line:
                comment_block = True

            if comment_block and "#" not in line:
                pupil_logic_output.write("\n")
                comment_block = False

            if comment_block:
                pupil_logic_output.write(line)
