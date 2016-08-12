import argparse
from classes.Helpers import *
from chewbaccaFunctions import *
from multiprocessing import Pool



# Program Version
version = "0.01"
# Time format for printing
FORMAT = "%(asctime)s  %(message)s"
# Date format for printing
DATEFMT = "%m/%d %H:%M:%S"

# TODO add output file option to all functions, and rename/move all the output files.
# rm -r rslt/;python chewbacca.py preprocess -n test -f ~/ARMS/testARMS/testData/20K_R2.fq -r ~/ARMS/testARMS/testData/20K_R1.fq -b /home/greg/ARMS/testARMS/testData/barcodes.txt -o rslt

"""
Supported operations:
    1. assemble
        pear + renameSequences.py
        mothur make.contigs + renameSequences.py

    2 demux
        fastx barcode splitter
        mothur split.groups

    3 trim (barcodes/adapters)
        mothur trim.seqs
        flexbar

    4 clean (sliding window)
        mothur trim.seqs
        trimmomatic

    5 dereplicate
        mothur unique.seqs
        ~/ARMS/bin/usearch7.0.1090

    6 align
        mothur align.seqs

    7 split
        splitKperFasta.py

    8 macsealign
        macse
        macse

    9 cluster
        vsearch derep_full_length

    9.5 chimeras
        mothur uchime.chimeras

    10 biocode (closed ref)
        vsearch usearch_global

    11 NCBI    (closed ref)
        ~/bin/vsearch/bin/vsearch-1.1.1-linux-x86_64

    12 buildmatrix
        mothur Make.biom
        ~/bin/builMatrix.py
"""

# TODO parser args should probably live next to their program strings (I.E. in Program Runner or another class)
def main(argv):
    """Parses command line args, builds an argparse.ArgumentParser, and runs the chosen command.
        Otherwise, prints usage.

    :param argv: Command line arguments as a list of strings
    """
    parser = argparse.ArgumentParser(description="arms description", epilog="arms long description")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
    parser.add_argument("--verbose", default=True, help="increase output verbosity", action="store_true")
    parser.add_argument('-t', '--threads', type=int, default=1)
    parser.add_argument('--dryRun', default=False)
    subparsers = parser.add_subparsers(dest='action', help='Available commands')


    # =============================================
    # ==  1 Assemble Reads using mothur or pear  ==
    # =============================================
    # "pear": programPaths["PEAR"] + " -f \"%s\" -r \"%s\" -o \"%s\" -j %d ",
    #
    #"make.contigs": "mothur \'#make.contigs(ffastq=%s, rfastq=%s, bdiffs=1, pdiffs=2, oligos=%s, \
    #                                 processors=%s)\'",
    parser_assemble = subparsers.add_parser('assemble')
    parser_assemble.add_argument('-f', '--input_f', required=True, help="Forward Fastq Reads (file or folder)")
    parser_assemble.add_argument('-r', '--input_r', required=True, help="Reverse Fastq Reads (file or folder)")
    parser_assemble.add_argument('-n', '--name',    required=True, help="Assembled File Prefix")
    parser_assemble.add_argument('-o', '--outdir',  required=True, help="Directory where outputs will be saved")
    parser_assemble.add_argument('-p', '--program', required=True, help="The name of the program to use.  \
                                                                        Either 'mothur' or 'pear' ")
    parser_assemble.set_defaults(func=assemble)

    # for mothur assembler
    mothur_assembler = parser_assemble.add_argument_group('mothur', 'Mothur options')
    mothur_assembler.add_argument('-g', '--oligos',  help="Oligos file with barcode and primer sequences")
    mothur_assembler.add_argument('-bd', '--bdiffs', help="# of allowed barcode mismatches")
    mothur_assembler.add_argument('-pd', '--pdiffs', help="# of allowed primer mismatches")

    # for pear assembler
    pear_assembler = parser_assemble.add_argument_group('pear', 'Pear options')
    pear_assembler.add_argument('-t', '--threads',   type=int, help="The number of threads to use (default is 1")


    # ======================================
    # ==  2  Split by barcode with FastX  ==
    # ======================================
    # "barcode.splitter": "cat \"%s\" | " + programPaths["FASTX"] + "fastx_barcode_splitter.pl  --bcfile \"%s\" \
    #                                    -prefix \"%s\" --suffix .fastq --bol --mismatches 1",
    parser_demux = subparsers.add_parser('demux_samples')
    parser_demux.add_argument('-i', '--input', required=True, help="Input fasta/fastq")
    parser_demux.add_argument('-b', '--barcodes', required=True,
                              help="Tab delimted files of barcodes and their samples")
    parser_demux.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_demux.set_defaults(func=splitOnBarcodes)


    # ===================================================
    # ==  3 Rename reads serially with renameSequences  ==
    # ===================================================
    # renameSequences(input, output)
    parser_rename = subparsers.add_parser('rename')
    parser_rename.add_argument('-i', '--input', required=True, help="Input file or directory")
    parser_rename.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_rename.add_argument('-f', '--filetype', required=True, help="The filetype of the input files")
    parser_rename.set_defaults(func=renameSequences)


    # =============================================================
    # ==  4 Trims barcodes and adapters using mothur or flexbar  ==
    # =============================================================
    parser_trim = subparsers.add_parser('trim_adapters')
    parser_trim.add_argument('-i', '--input', required=True, help="Input Fasta/Fastq File")
    parser_trim.add_argument('-p', '--program', required=True, help="The name of the program to use")
    parser_trim.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_trim.set_defaults(func=trim)
    # Mothur
    # "trim.seqs":        "mothur \'#trim.seqs(fasta=\"%s\", oligos=\"%s\", maxambig=1, maxhomop=8, \
    #                                minlength=300, maxlength=550, bdiffs=1, pdiffs=2)\'",
    mothur_trim = parser_trim.add_argument_group('mothur', 'Mothur options')
    mothur_trim.add_argument('-g', '--oligos', help="Mothur oligos file")
    # flexbar
    #"flexbar":  "flexbar -r \"%s\" -t \"%s\" -ae \"%s\" -a \"%s\""
    flexbar_trim = parser_trim.add_argument_group('flexbar', 'flexbar options')
    flexbar_trim.add_argument('-b', '--barcodes', help="Barcodes file")
    flexbar_trim.add_argument('-a', '--adapters', help="Adapters file")


    # ======================================
    # ==  5 Clean Reads with Trimmomatic  ==
    # ======================================
    # Clean low-quality reads with trimmomatic
    # "trimomatic":       "java -jar ~/ARMS/programs/Trimmomatic-0.33/trimmomatic-0.33.jar SE \
    # -phred33 input output_cleaned.fastq SLIDINGWINDOW:%windowsize:%minAvgQuality MINLEN:%minLen"
    parser_trimmomatic = subparsers.add_parser('clean_seqs')
    parser_trimmomatic.add_argument('-i', '--input', required=True, help="Run Id")
    parser_trimmomatic.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_trimmomatic.add_argument('-m', '--minLen', type=int, default=200,
                                            help="Minimum length for cleaned sequences")
    parser_trimmomatic.add_argument('-w', '--windowSize', type = int, default=5,
                                            help="Size of the sliding window")
    parser_trimmomatic.add_argument('-q', '--quality', type = int, default=25,
                                            help="Minimum average quality for items in the sliding window")
    parser_trimmomatic.set_defaults(func=trimmomatic)


    # ============================================
    # ==  6 Dereplicate sequences with usearch  ==
    # ============================================
    # "usearch": programPaths["USEARCH"] + " -derep_fulllength \"%s\" -output \"%s\" -uc \"%s\"",
    parser_derep = subparsers.add_parser('dereplicate_fasta')
    parser_derep.add_argument('-i', '--input', required=True, help="Input fasta/fastq")
    parser_derep.add_argument('-o', '--outdir',  required=True, help="Directory where outputs will be saved")
    parser_derep.set_defaults(func=dereplicate)


    # ==============================================
    # ==  7 Partition fastas with splitKperFasta  ==
    # ==============================================
    # splitK(inputFasta, prefix, nbSeqsPerFile, filetype):
    parser_split = subparsers.add_parser('partition')
    parser_split.add_argument('-i', '--input', required=True, help="Input fasta file to split")
    parser_split.add_argument('-o', '--outdir',  required=True, help="Directory where outputs will be saved")
    parser_split.add_argument('-c', '--chunksize', type=int, required=True, help="Chunksize.")
    parser_split.add_argument('-f', '--filetype', required=True, help="Filetype of the files to be partitioned")
    parser_split.set_defaults(func=partition)


    # =================================
    # ==  8 Align Reads with Mothur  ==
    # =================================
    #"align.seqs": "mothur \'#align.seqs(candidate=%s, template=%s, flip=t)\'",
    parser_mothuralign = subparsers.add_parser('align_seqs')
    parser_mothuralign.add_argument('-i', '--input', required=True, help="Fasta file containing the reads to align")
    parser_mothuralign.add_argument('-r', '--ref', required=True, help="Reference file containing known sequences")
    parser_mothuralign.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_mothuralign.set_defaults(func=align_mothur)
    

    # ================================
    # ==  9 Align Reads with MACSE  ==
    # ================================
    # "macse_align":      "java -jar " + programPaths["MACSE"] + " -prog enrichAlignment  -seq \"%s\" -align \
    #                                \"%s\" -seq_lr \"%s\" -maxFS_inSeq 0  -maxSTOP_inSeq 0  -maxINS_inSeq 0 \
    #                                -maxDEL_inSeq 3 -gc_def 5 -fs_lr -10 -stop_lr -10 -out_NT \"%s\"_NT \
    #                                -out_AA \"%s\"_AA -seqToAdd_logFile \"%s\"_log.csv",
    parser_align = subparsers.add_parser('macseAlign')
    parser_align.add_argument('-i', '--input', required=True, help="Input fasta")
    parser_align.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_align.add_argument('-d', '--db', required=True, help="Database against which to align and filter reads")
    parser_align.set_defaults(func=align_macse)


    # ==========================================
    # ==  10 Cluster using vsearch and swarm  ==
    # ==========================================
    # "vsearch": program_paths["VSEARCH"] + "--derep_fulllength \"%s\" --sizeout --fasta_width 0  \
    #
    parser_align = subparsers.add_parser('cluster_seqs')
    parser_align.add_argument('-i', '--input', required=True, help="Input fasta")
    parser_align.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_align.set_defaults(func=cluster)


    # ====================================
    # ==  11 Find Chimeras with Mothur  ==
    # ====================================
    # "chmimera.uchime":  "mothur \'#chimera.uchime(fasta=\"%s\", name=\"%s\")\'",
    parser_chimera = subparsers.add_parser('uchime')
    parser_chimera.add_argument('-i', '--input', required=True, help="Input Fasta File to clean")
    parser_chimera.add_argument('-o', '--outdir',  required=True, help="Directory where outputs will be saved")
    parser_chimera.add_argument('-p', '--program', required=False, default="uchime",
                                help="Program for detecting and removing chimeras. Default is uchime")
    refType = parser_chimera.add_mutually_exclusive_group(required=True)
    refType.add_argument('-n', '--names', help="Names file to reference")
    refType.add_argument('-d', '--refdb', help="Database file to reference")
    parser_chimera.set_defaults(func=findChimeras)


    # ==========================================
    # ==  12 Closed Ref Picking with BIOCODE  ==
    # ==========================================
    # --usearch_global  ../9_p_uchime/seeds.pick.fasta  --db ../data/BiocodePASSED_SAP.txt --id 0.9 \
    #	--userfields query+target+id+alnlen+qcov --userout out  --alnout alnout.txt
    parser_biocode = subparsers.add_parser('query_biocode')
    parser_biocode.add_argument('-i', '--input', required=True, help="Input Fasta File to clean")
    parser_biocode.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parser_biocode.set_defaults(func=queryBiocode)


    # =======================================
    # ==  13 Closed Ref Picking with NCBI  ==
    # =======================================
    # --usearch_global ../9_p_uchime/seeds.pick.fasta  --db /home/mahdi/refs/COI_DOWNLOADED/COI.fasta -id 0.9 \
    #          --userfields query+target+id+alnlen+qcov --userout out --alnout alnout.txt --userfields query+target+id+alnlen+qcov
    parcer_ncbi = subparsers.add_parser('query_ncbi')
    parcer_ncbi.add_argument('-i', '--input', required=True, help="Input Fasta File to clean")
    parcer_ncbi.add_argument('-o', '--outdir', required=True, help="Directory where outputs will be saved")
    parcer_ncbi.set_defaults(func=queryNCBI)


    # =======================================
    # ==  xx Remove sequences with Mothur  ==
    # =======================================
    # "remove.seqs": "mothur \'#remove.seqs(accnos=%s, %s)\'",
    parser_chimera = subparsers.add_parser('removeSeqs')
    parser_chimera.add_argument('-i', '--input', required=True, help="Input to clean")
    parser_chimera.add_argument('-a', '--accnos', required=True, help="Accnos listing sequences to remove")
    parser_chimera.add_argument('-o', '--outdir',  required=True, help="Directory where outputs will be saved")
    parser_chimera.add_argument('-f', '--filetype', required=True, help="Input file type.  Can be 'fasta', 'list',\
                                'groups','names','count', or 'alnReport'")
    parser_chimera.set_defaults(func=removeSeqs)

    # ===============================
    # ==  Screen seqs with Mothur  ==
    # ===============================
    # outputs: *.good.fasta and *.bad.accnos
    # "screen.seqs": "mothur \'#screen.seqs(fasta=%s, %s)\'",
    parser_screen= subparsers.add_parser('screen')
    parser_screen.add_argument('-i', '--input', required=True, action ='store',
                               help="File path to the file to clean")
    parser_screen.add_argument('-o', '--outdir', help="File path to your output directory")
    # optional filters
    parser_screen.add_argument('--start', help="Maximum allowable sequence starting index")
    parser_screen.add_argument('--end', help="Minimum allowable sequence ending index")
    parser_screen.add_argument('--minlength', help="Minimum allowable sequence length")
    parser_screen.add_argument('--maxlength', help="Maximum allowable sequence length")
    parser_screen.add_argument('--maxambig', help="Maxmimum number of allowed ambiguities")
    parser_screen.add_argument('--maxn', help="Maximum number of allowed N's")
    parser_screen.add_argument('--maxhomop', help="Maximum allowable homopolymer length")

    # optional aux files to update
    parser_screen.add_argument('-g', '--groups', help="Groups file to update")
    parser_screen.add_argument('-n', '--names', help="Names file to update")
    parser_screen.add_argument('-r', '--alnReport', help="Alignment report to update")
    parser_screen.add_argument('-c', '--contigsReport', help="Contigs report to update")
    parser_screen.add_argument('-s', '--summaryFile', help="SummaryFile to update")
    parser_screen.set_defaults(func=screenSeqs)

    # ============================================
    # ==   Prescreen sequences for frameshifts  ==
    # ============================================
    # screen(aln, caln)
    parser_prescreeen = subparsers.add_parser('prescreen')
    parser_prescreeen.add_argument('-a', '--aln_out_file', required=True, help=".aln output file from vsearch")
    parser_prescreeen.add_argument('-c', '--caln_userout_file', required=True, help="caln output file from vsearch.")
    parser_prescreeen.add_argument('-o', '--outdir',  required=True, help="Directory where outputs will be saved")
    parser_prescreeen.set_defaults(func=prescreen)


    # ==============================
    # ==  Convert fastq to fasta  ==
    # ==============================
    # "make.fasta":       "mothur \'#fastq.info(fastq=%s,fasta=T)\'"
    parser_toFasta = subparsers.add_parser('makeFasta')
    parser_toFasta.add_argument('-i', '--inputFastq', required=True, help="Input Fastq File")
    parser_toFasta.set_defaults(func=makeFasta)


    # ==============================
    # ==  Convert fasta to fastq  ==
    # ==============================
    # "make.fastq":       "mothur \'#make.fastq(fasta=%s,qfile=%s)\'",
    parser_toFastq = subparsers.add_parser('makeFastq')
    parser_toFastq.add_argument('-i', '--inputFasta', required=True, help="Input Fasta File")
    parser_toFastq.add_argument('-q', '--inputQual', required=True, help="Input qual File")
    parser_toFastq.set_defaults(func=makeFastq)


    # Drop short reads
    parser_dropShort = subparsers.add_parser('dropShort')
    parser_dropShort.add_argument('-n', '--name', required=True, help="Run Id")
    parser_dropShort.add_argument('-i', '--inputFasta', required=True, help="Clean inputs File")
    parser_dropShort.add_argument('-f', '--namesFile', required=True, help="Updated names file")
    parser_dropShort.add_argument('-l', '--minLenght', required=True, help="Min. length to keep")
    # todo -o is resereved for outdir
    # parser_dropShort.add_argument('-o', '--outFasta', required=True, help="Output file filtered on lenght")
    parser_dropShort.add_argument('-s', '--outNames', required=True, help="Updated names file")
    parser_dropShort.set_defaults(func=dropShort)


    # Todo remove this
    testParser = subparsers.add_parser('test')
    testParser.add_argument('-p', '--program',  help="Input Fasta File")
    group1 = testParser.add_argument_group("group1","G1help")
    group1.add_argument('-x', '--arg1', help="arg1 text")
    group2 = testParser.add_argument_group("group2", "G1help")
    group2.add_argument('-y', '--arg2', help="arg2 text")
    testParser.set_defaults(func=test)

    global args, pool
    args, unknown = parser.parse_known_args()
    if unknown:
        print "\nIgnoring unknown args: " + ', '.join(['%s']*len(unknown))% tuple(unknown)
    if args.verbose:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt=DATEFMT)
    else:
        logging.basicConfig(format=FORMAT, level=logging.ERROR, datefmt=DATEFMT)

    printVerbose.VERBOSE = args.verbose
    printVerbose("Running with %s process(es)" % args.threads)
    pool = Pool(args.threads)
    logging.debug("Initial ARGS are: %s", args)
    print("\t\t")
    dryRun = args.dryRun
    args.func(args, pool)

    pool.close()
    pool.join()


if __name__ == "__main__":
    main(sys.argv)
