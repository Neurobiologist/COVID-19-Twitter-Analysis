#!/bin/bash -l

# Set SCC project
#$ -P caad

# Specify hard time limit for the job. 
#   The job will be aborted if it runs longer than this time.
#   The default time is 12 hours
#$ -l h_rt=24:00:00

# Request 4 cores
#$ -pe omp 4

# Send an email when the job finishes or if it is aborted.
#$ -m beas

# Give job a name
#$ -N data-24h-4core-test

# Combine output and error files into a single file
#$ -j y

# Specify the output file name
#$ -o data-24h-4core-test.qlog

# Keep track of information related to the current job
echo "=========================================================="
echo "Start date : $(date)"
echo "Job name : $JOB_NAME"
echo "Job ID : $JOB_ID  $SGE_TASK_ID"
echo "=========================================================="

module load python3
module load miniconda
module load pigz
module load jq
conda activate /projectnb/caad/meganmp/.conda/env
pip install -r /projectnb/caad/meganmp/analysis/requirements.txt
python /projectnb/caad/meganmp/analysis/location-filter.py
