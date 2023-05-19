# nf-core/ampliseq

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
- Multiple run per sample?
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
