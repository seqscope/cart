#! /bin/zsh
#SBATCH --job-name=convert-hd30-hml22-incol
#SBATCH --mail-user=yonghah@umich.edu
#SBATCH --mail-type=BEGIN,END
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --partition=standard
#SBATCH --output=/home/%u/%j-%x.log
#SBATCH --mem-per-cpu=8000m
#SBATCH --account=hmkang0
#SBATCH --error=/home/%u/error-%j-%x.log
#SBATCH --get-user-env

echo 'started'

export STHOME=/home/yonghah/repo/geneus_loci
export DATASET=HD30-HML22-InCol
export STDATA=/scratch/hmkang_root/hmkang0/shared_data/NGST-sDGEvelo
export OUTDIR=/scratch/hmkang_root/hmkang0/yonghah
convert -d $STDATA/$DATASET -o $OUTDIR/$DATASET -m $OUTDIR/$DATASET/metadata-lane1.yaml -c 1 
