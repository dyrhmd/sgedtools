#! /usr/bin/python

""" Created on 21/08/20 by jdutheil

    Test if groups in one SGED file are include in ones from a second file.
"""

import getopt, sys
import pandas

cmd_args = sys.argv
arg_list = cmd_args[1:]

unix_opt = "s:t:o:g:h:r:c"
full_opt = [
    "sged1=",
    "sged2=",
    "output=",
    "group=",
    "group1=",
    "group2=",
    "result=",
    "csv",
]
try:
    arguments, values = getopt.getopt(arg_list, unix_opt, full_opt)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

tabsep = True  # TSV by default
group_col1 = "Group"
group_col2 = "Group"
result_col = "Inclusion"
for arg, val in arguments:
    if arg in ("-s", "--sged1"):
        sged_file1 = val
        print("First SGED file: %s" % sged_file1)
    elif arg in ("-t", "--sged2"):
        sged_file2 = val
        print("Second SGED file: %s" % sged_file2)
    elif arg in ("-o", "--output"):
        output_file = val
        print("Output file: %s" % output_file)
    elif arg in (
        "-g",
        "--group",
        "--group1",
    ):  # Note: if only this arg is passed, group col name is assumed to be identical in both files
        group_col1 = val
        print("Coordinates are in column: %s" % group_col1)
    elif arg in ("-h", "--group2"):
        group_col2 = val
        print("Coordinates for second file are in column: %s" % group_col2)
    elif arg in ("-r", "--result"):
        result_col = val
        print("Results of inclusion test are in column: %s" % result_col)
    elif arg in ("-c", "--csv"):
        tabsep = False

if tabsep:
    print("SGED file is in TSV format")
    delim = "\t"
else:
    print("SGED file is in CSV format")
    delim = ","

# Function that tests how two groups ovelap.
# Groups are provided as strings ([1;2;3]).
# The function is not symetric, it test whether group1 in included in group2, not the other way round.
def compare_groups(group1, group2):
    g1 = group1[1:-1].split(";")
    g2 = group2[1:-1].split(";")
    g1 = [x.strip() for x in g1]  # remove leading and trailing spaces
    g2 = [x.strip() for x in g2]
    test = [x in g2 for x in g1]
    if all(test):
        return "yes"
    elif any(test):
        return "partial"
    else:
        return "no"


# Start parsing
with open(sged_file1) as csv_file1:
    df1 = pandas.read_csv(csv_file1, sep=delim, dtype=str, comment="#")
with open(sged_file2) as csv_file2:
    df2 = pandas.read_csv(csv_file2, sep=delim, dtype=str, comment="#")

inc_test = [None] * len(df1)
test_groups = df2[group_col2].tolist()
for i in range(len(df1)):
    group1 = df1.loc[i, group_col1]
    results = [compare_groups(group1, test) for test in test_groups]
    test1 = [x == "yes" for x in results]
    res = "no"
    if any(test1):
        res = "yes"
    else:
        test2 = [x == "partial" for x in results]
        if any(test2):
            res = "partial"
    inc_test[i] = res


df1[result_col] = inc_test

# Write results:
df1.to_csv(output_file, sep=delim, na_rep="NA", index=False)

print("Done.")
