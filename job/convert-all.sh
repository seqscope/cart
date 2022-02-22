#! /bin/zsh
#SBATCH --job-name=convert-hd30-hml22-incol
#SBATCH --mail-user=yonghah@umich.edu
#SBATCH --mail-type=BEGIN,END
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --partition=standard
#SBATCH --output=/home/%u/log/%j-%x.log
#SBATCH --mem-per-cpu=64000m
#SBATCH --account=hmkang0
#SBATCH --error=/home/%u/log/error-%j-%x.log
#SBATCH --get-user-env


echo 'started'

export STHOME=/home/yonghah/repo/geneus_loci
export DATASET=HD30-HML22-InCol
export CONTAINER=~/simg/gdal_alpine-normal-latest.sif 
# export STDATA=/scratch/hmkang_root/hmkang0/shared_data/NGST-sDGEvelo/HD30-HML22-InCol
convert -o ./tiles -m metadata.yaml -c 1 

echo 'merge'
find ./tiles -type f -print0 | xargs -r0 singularity exec $CONTAINER ogrmerge.py -o ./merged.gpkg -f GPKG -single -nln all

echo 'filter'
filter -i merged.gpkg -o filtered.gpkg -m $STHOME/config/markers.yaml -n $DATASET -s $CONTAINER 
