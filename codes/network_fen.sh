#!/bin/bash 

#SBATCH --job-name=network
#SBATCH --partition=dept_cpu
#SBATCH --nodes=1
#SBATCH --ntasks=24
#SBATCH --ntasks-per-node=24
##SBATCH --nodelist=n092.dcb.private.net
##SBATCH --time=00:05:00 

# current (working) direcotry
work_dir=$(pwd)
# username
user=$(whoami)
# directory name where job will be run (on compute node)
job_dir="${user}_${SLURM_JOB_ID}.dcb.private.net"

# creating directory on /scr folder of compute node
mkdir /scr/$job_dir
# change to the newly created directory
cd /scr/$job_dir
# copy the submit file (and all other related files/directories)
rsync -ra ${work_dir}/* .

module load anaconda/3
source activate py2
# "srun" command is part of slurm package & stress-ng is a command to put stress on node
srun python test.py

# put hostname of compute node in a file
hostname > hostname.txt
# put date and time of finished job in a file
date > date.txt

# copy back all the files/directories back to the slurm head node
rsync -a ./data/netdist/netdist.pkl ${work_dir}