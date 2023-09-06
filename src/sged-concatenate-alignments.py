#! /usr/bin/python

""" Created on 02/12/21 by jdutheil

    Merge a series of sequence alignments and output a SGED file with coordinates.
"""

import getopt, sys
import pandas
from Bio import AlignIO

cmd_args = sys.argv
arg_list = cmd_args[1:]

unix_opt = "1:2:l:f:a:o:ch"
full_opt = [
    "aln1=",
    "aln2=",
    "aln-list",
    "format=",
    "output-aln=",
    "output-sged=",
    "csv",
    "help"
]

def usage() :
    print(
"""
sged-concatenate-alignments

Available arguments:
    --aln1 (-1): Input first single input alignment file.
    --aln2 (-2): Input second single input alignment file.
    --aln-list (-l): File with list of input alignment files.
        Required if --aln1 and --aln2 are not provided.
        On path (absolute or relative to current directory) per line.
    --format (-f): Input alignment format, any recognized by Bio::AlignIO
        (see https://biopython.org/wiki/AlignIO).
        All alignments must be in the same format.
    --output-aln (-o): Output concatenated alignment file (required).
        Same format as the input one.
    --output-sged (-o): Output SGED file (required).
        The output file will contain a Group column with concatenated alignment
        positions in the order specified by the input options/list.
        The following columns are also added:
         * AlnPos: alignment position relative to the input single alignment.
         * AlnIndex: index of the input alignment in the input list.
         * AlnId: path/name of the corresponding input alignment.
    --csv (-c): Input SGED file is with comas instead of tabs (default)
    --help (-h): Print this message.
"""
    )
    sys.exit()

try:
    arguments, values = getopt.getopt(arg_list, unix_opt, full_opt)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

tabsep = True  # TSV by default
aln_paths = []
output_aln_file = "concat"
output_sged_file = "concat.sged"
aln_format = "fasta"
for arg, val in arguments:
    if arg in ("-1", "--aln1"):
        aln_paths.append(val)
    elif arg in ("-2", "--aln2"):
        aln_paths.append(val)
    elif arg in ("-l", "--aln-list"):
        with open(val, "r") as path_file:
            aln_paths = path_file.readlines()
    elif arg in ("-f", "--format"):
        aln_format = val  # Any format supported by BioPython
        print("Sequence files in: %s" % aln_format)
    elif arg in ("-a", "--output-aln"):
        output_aln_file = val
        print("Output concatenated alignment file: %s" % output_aln_file)
    elif arg in ("-o", "--output-sged"):
        output_sged_file = val
        print("Output SGED file: %s" % output_sged_file)
    elif arg in ("-c", "--csv"):
        tabsep = False
    elif arg in ("-h", "--help"):
        usage()

if tabsep:
    print("SGED file is in TSV format.")
    delim = "\t"
else:
    print("SGED file is in CSV format.")
    delim = ","

# Check required arguments
if not 'sged_file' in globals():
   usage()
if not 'output_file' in globals():
   usage()

# Start parsing
global_pos = []
local_pos = []
aln_nb = []
aln_id = []
concat_aln = None
pos_count = 0

for aln_count, aln_path in enumerate(aln_paths):
    print("Reading input alignment %s." % aln_path)
    aln = AlignIO.read(aln_path, aln_format)
    aln.sort()
    if concat_aln is None:
        concat_aln = aln
    else:
        concat_aln = concat_aln + aln
    for i in range(aln.get_alignment_length()):
        pos_count = pos_count + 1
        global_pos.append("[%i]" % pos_count)
        local_pos.append("[%i]" % (i + 1))
        aln_nb.append(aln_count + 1)
        aln_id.append(aln_path)

# Write concatenated alignment:
with open(output_aln_file, "w") as aln_file:
    AlignIO.write(concat_aln, aln_file, aln_format)

# Write SGED file:
with open(output_sged_file, "w") as csv_file:
    d = dict(Group=global_pos, AlnPos=local_pos, AlnIndex=aln_nb, AlnId=aln_id)
    df = pandas.DataFrame(data=d)
    df.to_csv(csv_file, index=False, sep=delim)

print("Done.")