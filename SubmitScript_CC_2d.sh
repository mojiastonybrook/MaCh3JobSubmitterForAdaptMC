#!/bin/bash
#SBATCH --mail-user=mo.jia@stonybrook.edu
#SBATCH --mail-type=ALL
#SBATCH --job-name=JOBNAME
#SBATCH --output=SUBMITSCRIPTOUTPUT
#SBATCH --error=ERRORFILE
#SBATCH --account=rpp-blairt2k
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:v100l:1
#SBATCH --time=48:00:00
#SBATCH --mem=30G
#SBATCH --array=ARRAY

srun EXECUTABLENAME
