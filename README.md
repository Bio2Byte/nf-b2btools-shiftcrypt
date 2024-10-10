ShiftCrypt Nextflow Pipeline
----------

This repository contains a Nextflow pipeline that integrates the Bio2Byte tool ShiftCrypt. ShiftCrypt is used for the prediction of NMR chemical shifts using a variety of atom sets. This pipeline facilitates the execution of ShiftCrypt on NMR-related data files in either NEF or NMR-STAR format, streamlining data processing and prediction tasks.

# Workflow Overview

The pipeline is designed to run the ShiftCrypt prediction tool with the following key parameters:

- *Input Directory*: The pipeline processes files from the specified input directory, supporting both .nef and .nmr file formats.
- *Model:* The user can select one of three atom set models for prediction:
  - *Model 1*: Full atom set.
  - *Model 2*: H, HA, CA, N, CB, C atoms.
  - *Model 3*: CA, N, H atoms.
- *Original Numbering*: Whether to use the original sequence numbering in the prediction (default is true).
- *File Type*: Specify whether the input is in NMR-STAR format (default is false for NEF files).

The core of the workflow is the `PREDICT_SHIFTCRYPT` module, which handles the execution of ShiftCrypt for each input file. The input files are automatically identified and processed, with results being output to a specified directory.

## Pipeline Structure

```
params.inputDir = params.inputDir ?: "./data"
params.outputDir = params.outputDir ?: "./results"

params.model = params.model ?: "1"
params.isModelStar = params.isModelStar ?: false
params.originalNumbering = params.originalNumbering ?: true

include { PREDICT_SHIFTCRYPT } from "$projectDir/modules/bio2byte"

input_files = Channel.fromPath("${params.inputDir}/*.{nef,nmr}")
    .map { file -> tuple(file.baseName, file) }

workflow {
    main:
        PREDICT_SHIFTCRYPT(
            params.model,
            params.isModelStar,
            params.originalNumbering,
            input_files
        )
}
```

# Running the Pipeline

## Requirements

- *Nextflow*: The pipeline is written in Nextflow DSL2 and requires Nextflow to be installed.
- *Docker* or Singularity: Containers are required to run the pipeline in a reproducible environment.

## Commands

To run the ShiftCrypt pipeline from this repository, follow these steps:

	1.	Clone the repository:
```bash
git clone https://github.com/Bio2Byte/nf-b2btools-shiftcrypt.git
cd nf-b2btools-shiftcrypt
```

	2.	Prepare your input data files. Place your .nef or .nmr files in the input directory, or specify a custom input directory using the --inputDir parameter.
	3.	Run the pipeline with Nextflow:
```bash
nextflow run https://github.com/Bio2Byte/nf-b2btools-shiftcrypt \
    --inputDir ./data \
    --outputDir ./results \
    --model 1 \
    --isModelStar false \
    --originalNumbering true
```

- `–inputDir`: Directory containing input files (.nef or .nmr).
- `–outputDir`: Directory to store the results.
- `–model`: Choose from model 1, 2, or 3 based on atom set.
- `–isModelStar`: Set to true if using NMR-STAR files, otherwise leave as false for NEF files.
- `–originalNumbering`: Use true to retain original sequence numbering.

	4.	Monitor the pipeline execution through the console output or view logs in the working directory.

## Output

The pipeline will output the ShiftCrypt prediction results into the directory specified by the `--outputDir` parameter. The results for each input file will be stored in JSON format.

# License

TBD
