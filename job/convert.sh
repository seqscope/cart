#! /bin/zsh
#SBATCH --job-name=convert-LIVER-ALL-test
#SBATCH --mail-user=yonghah@umich.edu
#SBATCH --mail-type=BEGIN,END
#SBATCH --cpus-per-task=2
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --partition=standard
#SBATCH --output=/home/%u/%x-%j.log
#SBATCH --mem-per-cpu=64000m
#SBATCH --account=hmkang0
#SBATCH --error=/home/%u/%x-%j-error.log
#SBATCH --get-user-env

echo 'started'


export STHOME=/home/yonghah/repo/geneus_loci
export STDATA=/scratch/hmkang_root/hmkang0/shared_data/NGST-sDGE/RD2-Liver-All
export OUTDIR=/scratch/hmkang_root/hmkang0/yonghah
python3 $STHOME/geneus_loci/convert.py -d $STDATA -o $OUTDIR/RD2-Liver-All.gpkg -f GPKG
