#!/bin/bash
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
# module load python/3.9.1 singularity aws-cli/2

# before running this
source /home/yonghah/venv/cart/bin/activate

# export DATASET=HD30-inj-colon-comb
export CONTAINER=/home/yonghah/simg/gdal_alpine-normal-latest.sif
export sdge_dir=/Users/yonghah/data/seqscope/HD31-HMKYV-human-L2/sge
# export marker_yaml=/home/yonghah/repo/cart/config/markers.yaml
# export histology_path=s3://seqscope-hist2sdge/hd30-inj-colon-comb/referenced/histology.tif
export factor_result=/Users/yonghah/data/seqscope/HD31-HMKYV-human-L2/lda/fit_result.tsv.gz
export output_dir=/Users/yonghah/data/seqscope/HD31-HMKYV-human-L2/output
export BUCKET=hd31-hmkyv-human-l2


echo 'convert sDGE'
  
python -m cart.convert \
  -i $sdge_dir \
  -o $output_dir/interim/vector-sdge/sge.tsv.gz

singularity exec $CONTAINER ogr2ogr -f Flatgeobuf $output_dir/vector/full_sdge.fgb \
  /vsigzip/$output_dir/interim/vector-sdge/sge.tsv.gz \
  -oo X_POSSIBLE_NAMES=x -oo Y_POSSIBLE_NAMES=y \
  -oo KEEP_GEOM_COLUMNS=NO -a_srs "EPSG:3857"

mkdir -p $output_dir/raster
singularity exec $CONTAINER gdal_rasterize -a cnt_total -add -tr 2 2 \
$output_dir/vector/full_sdge.fgb \
$output_dir/raster/count_sdge.tif

singularity exec $CONTAINER gdaldem hillshade -z 50 -compute_edges -alg Horn -igor \
  $output_dir/raster/count_sdge.tif $output_dir/raster/hillshade.tif

singularity exec $CONTAINER gdal2tiles.py -z 9-19 \
$output_dir/raster/hillshade.tif $output_dir/tile/raster-count

aws s3 sync \
$output_dir/tile/raster-count s3://$BUCKET/tile/raster-count \
--profile default 


echo 'convert factor'

python -m cart.factor \
-i $factor_result \
-o $output_dir/vector/factor.gpkg \
-s 1 -r 1.5

echo 'create vector tiles for factors'
rm -rf $output_dir/tile/vector-factor
singularity exec $CONTAINER ogr2ogr -f MVT $output_dir/tile/vector-factor -progress \
$output_dir/vector/factor.gpkg \
-dsco MINZOOM=9 -dsco MAXZOOM=14 \
-dsco MAX_SIZE=2500000 -dsco MAX_FEATURES=1500000


echo 'upload vector tiles'

aws s3 sync --metadata-directive REPLACE --content-encoding 'gzip' \
$output_dir/tile/vector-factor s3://$BUCKET/tile/vector-factor --profile default \
--exclude 'metadata.json'

aws s3 cp $output_dir/tile/vector-factor/metadata.json \
s3://$BUCKET/tile/vector-factor/metadata.json \
--profile default

