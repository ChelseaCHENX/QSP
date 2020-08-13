#!/bin/bash 

#SBATCH --job-name=network
#SBATCH --partition=dept_cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=60
#SBATCH --time=24:00:00

##SBATCH --ntasks-per-node=60
##SBATCH --nodelist=n092.dcb.private.net
 

# current (working) direcotry
work_dir=/net/dali/home/bahar/fangyuan/projects/qsp
cd $work_dir
# # username
# user=$(whoami)
# # directory name where job will be run (on compute node)
# job_dir="${user}_${SLURM_JOB_ID}.dcb.private.net"

# # creating directory on /scr folder of compute node
# mkdir /scr/$job_dir
# # change to the newly created directory
# cd /scr/$job_dir
# # copy the submit file (and all other related files/directories)
# rsync -ra ${work_dir}/codes .
# rsync -ra ${work_dir}/data .

module load anaconda/3
source activate py2
# "srun" command is part of slurm package & stress-ng is a command to put stress on node
/net/dali/home/bahar/fangyuan/.conda/envs/py2/bin/python codes/test.py

# put hostname of compute node in a file
hostname > $work_dir/netdist/hostname.log
# put date and time of finished job in a file
date > $work_dir/netdist/date.log

# # copy back all the files/directories back to the slurm head node
# rsync -a ./data/netdist/netdist.pkl ${work_dir}