from align.align_clean import remove_refs_from_macse_out
from classes.ChewbaccaProgram import *
from classes.Helpers import *
from classes.ProgramRunner import *
from util.merge import merge_files


class Align_Clean_Program_Macse(ChewbaccaProgram):
    name = "macse"


    def execute_program(self):
        args = self.args
        self.align_clean_macse(args.input_f, args.db, args.samplesdir, args.outdir, args.threads)



    def align_clean_macse(self, input_f, ref, samplesdir, outdir, threads):
        """Removes non-nucleotide characters in MACSE aligned sequences for all fasta files in the samples directory
            (the samplesDir argument).

        :param input_f: File path to file or folder of files to clean.
        :param samplesdir: Filepath to the original, unaligned input files (the inputs to the macse aligner).
        :param ref: Filepath to the reference file used to align the input files.
        :param outdir: Filepath to the directory to write outputs to.
        :param pool: A fully-initalized multiprocessing.Pool object.
        """
        # "macse_format":     "java -jar " + programPaths["MACSE"] + "  -prog exportAlignment -align \"%s\" \
        #                                  -charForRemainingFS - -gc_def 5 -out_AA \"%s\" -out_NT \"%s\" -statFile \"%s\""
        makeDirOrdie(outdir)
        inputs = getInputFiles(input_f)
        pool = init_pool(min(len(inputs), threads))
        printVerbose("\t %s Processing MACSE alignments")
        samplesList = getInputFiles(samplesdir)
        parallel(runProgramRunnerInstance, [ProgramRunner(ProgramRunnerCommands.MACSE_FORMAT,
                                                          ["%s/%s_NT" % (input_f, getFileName(sample)),
                                                           "%s/%s_AA_macse.fasta" % (outdir, getFileName(sample)),
                                                           "%s/%s_NT_macse.fasta" % (outdir, getFileName(sample)),
                                                           "%s/%s_macse.csv" % (outdir, getFileName(sample))],
                                                          {"exists": []}) for sample in samplesList], pool)
        printVerbose("\tCleaning MACSE alignments")

        printVerbose("Processing %s samples..." % len(samplesList))
        nt_macse_outs = ["%s/%s_NT_macse.fasta" % (outdir, strip_ixes(sample)) for sample in samplesList]

        # Clean the alignments
        parallel(runPythonInstance, [(remove_refs_from_macse_out, input_, ref,
                                      "%s/%s" % (outdir, "%s_cleaned.fasta" % strip_ixes(input_)))
                                     for input_ in nt_macse_outs], pool)

        # Cat the cleaned alignments
        cleaned_alignments = getInputFiles(outdir, "*_cleaned.fasta")
        merge_files(cleaned_alignments, "%s/MACSE_OUT_MERGED.fasta" % outdir)

        aux_dir = makeAuxDir(outdir)
        aux_files = getInputFiles(outdir, "*", "MACSE_OUT_MERGED.fasta")
        bulk_move_to_dir(aux_files, aux_dir)
        cleanup_pool(pool)