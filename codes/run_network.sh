#!/bin/bash
module load anaconda/3
source activate py2

cd /net/dali/home/bahar/fangyuan/projects/qsp/codes
python test.py
# cd /net/dali/home/bahar/fangyuan/projects/qsp/codes; sbatch --cpus-per-task 60 --mem 80g -t 24:00:00 run_network.sh -o ../data/log/dist_drug.o -e ../data/log/dist_drug.e