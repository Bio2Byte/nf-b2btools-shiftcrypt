params.shiftcrypt_script = "$projectDir/bin/bio2byte/shiftcrypt.py"

process PREDICT_SHIFTCRYPT {
    tag "${input_file} ${model} ${isModelStar} ${originalNumbering}"
    conda "${projectDir}/modules/bio2byte/conda-env.yaml"

    publishDir "$params.outputDir", mode: 'copy'
    errorStrategy 'ignore'
    debug true

    input:
        val model
        val isModelStar
        val originalNumbering
        tuple val(sample_id), path(input_file)

    output:
        path "${sample_id}.json"
        path "${sample_id}.log"

    script:
    """
    python ${params.shiftcrypt_script} ${input_file} -m ${model} ${originalNumbering ? '-o' : ''} ${isModelStar ? '-s' : ''}  -f ${sample_id}.json -l ${sample_id}.log
    """

    stub:
    """
    touch ${sample_id}_prediction_output.json
    """
}
