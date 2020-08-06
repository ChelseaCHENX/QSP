# https://www.csb.pitt.edu/using-the-cluster/
cd /net/dali/home/bahar/fangyuan/projects/qsp
rsync -avzP fangyuan@mozart.csb.pitt.edu:/home/fangyuan/home2/projects/qsp/codes ./
rsync -avzP fangyuan@mozart.csb.pitt.edu:/home/fangyuan/home2/projects/qsp/data/network ./

module load anaconda/3
conda create --name py2 python=2.7
source activate py2
conda install numpy scipy networkx pandas