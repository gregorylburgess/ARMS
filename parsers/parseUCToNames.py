from collections import defaultdict
import sys

# TODO rename, these arent fasta files
def parseUCtoNames(input_uc_file, output_names_file):
    """Pulls the representative seed sequences from a .uc file and generates a .names file.

    :param input_uc_file: Filepath to the input .uc file.
    :param output_names_file: File path to the output .names file.
    :return: File path to the output .names file.
    """

    seeds = defaultdict(list)
    for line in open(input_uc_file, 'r'):
        data = line.split()
        if data[0] == "H":
            seeds[data[-1].replace(":", "_")].append(data[-2].replace(":", "_"))
        if data[0] == "S":
            seeds[data[8]] = [data[8]]

    with open(output_names_file, 'w')  as outFile:
        for key in seeds:
            outFile.write(key+"\t")
            outFile.write(" ".join(list(set(seeds[key]))))
            outFile.write("\n")
    return output_names_file


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: fastaA fastaB outfile"
    else:
        parseUCtoNames(*sys.argv[1:3])