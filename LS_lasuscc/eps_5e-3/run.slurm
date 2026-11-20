#!/bin/bash -l
#SBATCH --job-name=01ls
#SBATCH --account=pi-lgagliardi
#SBATCH --qos=lgagliardi
#SBATCH --time=238:00:00
#SBATCH --nodes=1
#SBATCH --partition=lgagliardi-ld,lgagliardi-hm,lgagliardi-amd
#SBATCH --mem-per-cpu=10G
#SBATCH --cpus-per-task=8
#SBATCH --error=lasuscc_alfefe.err

. setup_env_midway3.sh

python alfefe_lasuscc.py > lasuscc.out
