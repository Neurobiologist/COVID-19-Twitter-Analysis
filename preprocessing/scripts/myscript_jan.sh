#!/bin/bash -l

# Set SCC project
#$ -P caad

# Specify hard time limit for the job. 
#   The job will be aborted if it runs longer than this time.
#   The default time is 12 hours (6h/day)
#$ -l h_rt=72:00:00

# Request 1 core
#$ -pe omp 1

# Send an email when the job finishes or if it is aborted.
#$ -m beas

# Give job a name
#$ -N tweets_jan

# Combine output and error files into a single file
#$ -j y

# Specify the output file name
#$ -o tweets_jan.qlog

# Task Numbers
#$ -t 21-31

# Keep track of information related to the current job
echo "=========================================================="
echo "Start date : $(date)"
echo "Job name : $JOB_NAME"
echo "Job ID : $JOB_ID  $SGE_TASK_ID"
echo "=========================================================="

module load python3
python /analysis/preprocessing/location-filter-jan.py
