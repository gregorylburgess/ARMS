from classes.ChewbaccaCommand import ChewbaccaCommand
from util.Convert_Fastq_Fasta_Program_Chewbacca import Convert_Fastq_Fasta_Program_Chewbacca


class Convert_Fastq_Fasta_Command(ChewbaccaCommand):
    """Converts a Fastq-formatted file to a Fasta-formatted file.  Useful for reducing data size and preparing for
        fasta-only operations.

        **Inputs**:
            * A fastq file or a director conataining multiple fastq files .

        **Outputs**:
            * <filename>.fasta file(s) - Converted fasta files.

        **Example**:

        ::

            ./
                Data.fastq:
                    @Data_ID#1
                    AGACGCGGWACWGGWTGAACWGTWTAYCCYCCATCGATCGATCGTGRTTYTTYGGNCAYCCNGARGTNTA


        ``$ python chewbacca.py trim_adapters  -i Data.fasta -o rslt ``


        ::

            rslt/
                Data.fasta:
                    >Data_ID#1
                    AGACGCGGWACWGGWTGAACWGTWTAYCCYCCATCGATCGATCGTGRTTYTTYGGNCAYCCNGARGTNTA

    """
    supported_programs = [Convert_Fastq_Fasta_Program_Chewbacca]
    default_program = Convert_Fastq_Fasta_Program_Chewbacca
    command_name = "Convert Fastq to Fasta"
