"""
nf-core/ampliseq workflow
"""

import os
import subprocess
from pathlib import Path
from enum import Enum

from latch import small_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchAuthor, LatchFile, LatchMetadata, LatchParameter, LatchDir

class SeqType(Enum):
    paired = 'paired'
    single = 'single'

class SeqTech(Enum):
    illumina = 'illumina'
    novaseq = 'novaseq'
    pacbio = 'pacbio'
    iontorrent = 'iontorrent'

@small_task
def main_task(
    readsdir: LatchDir = LatchDir(
        "s3://ampliseq_16S/"
    ),
    seqtech: SeqTech = SeqTech.illumina,
    seqtype: SeqType = SeqType.paired,
    fprimer: str = "GTGYCAGCMGCCGCGGTAA",
    rprimer: str = "GGACTACNVGGGTWTCTAAT",
    itspe: bool = False,
    multi: bool = False,
    metafile: LatchFile = LatchFile(
        "s3://ampliseq_16S/metadata.tsv"
    )
) -> LatchDir:

    # directory of output
    local_dir = "/root/work/" 
    local_out = os.path.join(local_dir, "results")

    main_cmd = [
        "nextflow", "run",
            "nf-core/ampliseq", 
            "-profile", "charliecloud",
            "-work-dir", local_dir,
            "--input", readsdir.local_path,
            "--outdir", local_out,
    ]

    if fprimer and rprimer:
        main_cmd.append("--FW_primer")
        main_cmd.append(fprimer)
        main_cmd.append("--RV_primer")
        main_cmd.append(rprimer)
        
    if seqtype == 'single':
        main_cmd.append("--single_end")

    if seqtech == 'novaseq':
        main_cmd.append("--illumina_novaseq")
    elif seqtech == 'pacbio':
        main_cmd.append("--pacbio")
    elif seqtech == 'iontorrent':
        main_cmd.append("--iontorrent")

    
    if itspe:
        main_cmd.append("--illumina_pe_its")
    
    if multi:
        main_cmd.append("--multiple_sequencing_runs")
    
    if metafile:
        main_cmd.append("--metadata")
        main_cmd.append(metafile.local_path)

    subprocess.run(main_cmd, check=True)
    return LatchDir(local_out, f"latch:///ampliseq/results")


"""The metadata included here will be injected into your interface."""
metadata = LatchMetadata(
    display_name="nf-core/ampliseq workflow",
    documentation="",
    author=LatchAuthor(
        name="Juan Caballero",
        email="juan.caballero.perez@gmail.com",
        github="github.com/caballero",
    ),
    repository="https://github.com/caballero/latchbio-nf-ampliseq",
    license="",
    parameters={
        "readsdir": LatchParameter(
            display_name="Select the Fastq directory location",
            description="Specify the location of the fastq files.",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "seqtype": LatchParameter(
            display_name="Sequence type",
            description="Select if reads are paired or single ends",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "seqtech": LatchParameter(
            display_name="Sequence technology",
            description="Select reads tecnology: Illumina, Illimina Novaseq, PacBio, IonTorrent",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "fprimer": LatchParameter(
            display_name="Forward primer sequence",
            description="Sequence for the forward primer",
            placeholder="GTGYCAGCMGCCGCGGTAA",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "rprimer": LatchParameter(
            display_name="Reeverse primer sequence",
            description="Sequence for the reverse primer",
            placeholder="GGACTACNVGGGTWTCTAAT",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "multi": LatchParameter(
            display_name="Multiple runs per sample",
            description="Select if there are multiple runs per sample organized in subdirectories",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "itspe": LatchParameter(
            display_name="Paired ITS (Illumina)",
            description="Select if reads are paired-ends for ITS regions (only Illumina)",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "metafile": LatchParameter(
            display_name="Metadata file",
            description="Select metadata file",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),  
        
    },
    tags=[],
)


@workflow(metadata)
def run_wf(
    readsdir: LatchDir,
    seqtech: SeqTech,
    seqtype: SeqType,
    fprimer: str,
    rprimer: str,
    itspe: bool,
    multi: bool,
    metafile: LatchFile
) -> LatchDir:
    """nf-core/ampliseq

This is a port of the nf-core/ampliseq workflow for amplicon sequencing analysis workflow using DADA2 and QIIME2 to LatchBio.

https://nf-co.re/ampliseq/


The nfcore/ampliseq is a bioinformatics analysis pipeline used for amplicon sequencing, supporting denoising of any amplicon and, currently, taxonomic assignment of 16S, ITS, CO1 and 18S amplicons. Supported is paired-end Illumina or single-end Illumina, PacBio and IonTorrent data. Default is the analysis of 16S rRNA gene amplicons sequenced paired-end with Illumina.

----

## Inputs

- Fastq reads
- Sequence type [paired, single]
- Sequence technology [illumina, novaseq, pacbio, iontorrent]
- Paired ITS Illumina?
- Sequence forward primer
- Sequence reverse primer
- Multiple sequences?
- Metadata file

## Outputs

- Input - Input files
- Preprocessing
  - FastQC - Read quality control
  - Cutadapt - Primer trimming
  - MultiQC - Aggregate report describing results
- ASV inferrence with DADA2 - Infer Amplicon Sequence Variants (ASVs)
- Optional ASV filtering - Filter ASVs to optimize downstream analysis
  - Barrnap - Predict ribosomal RNA sequences and optional filtering
  - Length filter - Optionally, ASV can be filtered by length thresholds
  - ITSx - Optionally, the ITS region can be extracted
- Taxonomic classification with DADA2 - Taxonomic classification of (filtered) ASVs
  - assignSH - Optionally, a UNITE species hypothesis (SH) can be added to the taxonomy
- QIIME2 - Secondary analysis
  - Taxonomic classification - Taxonomical classification of ASVs
  - Abundance tables - Exported abundance tables
  - Relative abundance tables - Exported relative abundance tables
  - Barplot - Interactive barplot
  - Alpha diversity rarefaction curves - Rarefaction curves for quality control
  - Diversity analysis - High level overview with different diversity indices
  - ANCOM - Differential abundance analysis
- PICRUSt2 - Predict the functional potential of a bacterial community
- Read count report - Report of read counts during various steps of the pipeline
- Pipeline information - Report metrics generated during the workflow execution


## Workflow

By default, the pipeline currently performs the following:

- Sequencing quality control (FastQC)
- Trimming of reads (Cutadapt)
- Infer Amplicon Sequence Variants (ASVs) (DADA2)
- Predict whether ASVs are ribosomal RNA sequences (Barrnap)
- Taxonomical classification using DADA2 or QIIME2
- Excludes unwanted taxa, produces absolute and relative feature/taxa count tables and plots, plots alpha rarefaction curves, computes alpha and beta diversity indices and plots thereof (QIIME2)
- Calls differentially abundant taxa (ANCOM)
- Overall pipeline run summaries (MultiQC)
    """
    return main_task(
                readsdir = readsdir,
                seqtech = seqtech,
                seqtype = seqtype,
                fprimer = fprimer,
                rprimer = rprimer,
                itspe = itspe,
                multi = multi,
                metafile = metafile,
            )



"""
Add test data with a LaunchPlan. Provide default values in a dictionary with
the parameter names as the keys. These default values will be available under
the 'Test Data' dropdown at console.latch.bio.
"""
LaunchPlan(
    run_wf,
    "Test Data",
    {
        "readsdir": LatchDir(
            "s3://ampliseq_16S/"
        ),
        "seqtech": SeqTech.illumina,
        "seqtype": SeqType.paired,
        "fprimer": "GTGYCAGCMGCCGCGGTAA",
        "rprimer": "GGACTACNVGGGTWTCTAAT",
        "itspe": False,
        "multi": False,
        "metafile": LatchFile(
            "s3://ampliseq_16S/metadata.tsv"
        )
    },
)
