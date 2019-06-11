#!/bin/bash
#SBATCH --job-name=MYJOB
#SBATCH --output=%j.MYJOB.out
#SBATCH --error=%j.MYJOB.err
#SBATCH --partition=standard
#SBATCH --time=1-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=2048
##SBATCH --mail-type=END,FAIL
##SBATCH --mail-user=john.doe@rothamsted.ac.uk
#+
# Below here is the script itself
#-
module load <Python version>
virtualenv <Python version>
source <path to virtual env>/bin/activate
