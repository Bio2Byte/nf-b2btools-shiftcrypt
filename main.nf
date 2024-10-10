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
