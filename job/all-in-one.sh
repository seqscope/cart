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
module load python/3.9.1 singularity aws-cli/2

# before running this
source /home/yonghah/venv/cart/bin/activate

export DATASET=HD30-inj-colon-comb
export CONTAINER=/home/yonghah/simg/gdal_alpine-normal-latest.sif
export sdge_dir=/gpfs/accounts/hmkang_root/hmkang0/shared_data/NGST-sDGEvelo/HD30-inj-colon-comb
export marker_yaml=/home/yonghah/repo/cart/config/markers.yaml
export histology_path=s3://seqscope-hist2sdge/hd30-inj-colon-comb/referenced/histology.tif
export factor_result=/gpfs/accounts/hmkang_root/hmkang0/shared_data/tmp/LDA/HD30-inj-colon-comb/analysis/LDA_hexagon.nFactor_10.d_18.lane_2.2101_2102_2103_2104_2105_2106_2107_2108_2109_2110_2111_2112_2113_2114_2115_2116_2201_2202_2203_2204_2205_2206_2207_2208_2209_2210_2211_2212_2213_2214_2215_2216.fit_result.tsv.gz
export x0=-1579984
export output_dir=/home/yonghah/jobs/HD30-inj-colon-comb
export BUCKET=hd30-inj-colon-comb

echo 'metadata generation'

meta -n $DATASET -d $sdge_dir -o $output_dir/vector/metadata.yaml -l 2

echo 'convert sDGE'

python -m cart.convert -o $output_dir/interim/vector-sdge \
-m $output_dir/vector/metadata.yaml -c 1

find $output_dir/interim/vector-sdge -type f -print0 \
| xargs -r0 singularity exec $CONTAINER ogrmerge.py \
-o $output_dir/vector/full_sdge.fgb -f FlatGeobuf -single -nln all

echo 'filter marker genes'
rm -f $output_dir/vector/marker.gpkg
filter -i $output_dir/vector/full_sdge.fgb \
-o $output_dir/vector/marker.gpkg -m $marker_yaml -n $DATASET -s $CONTAINER

echo 'create vector tiles for marker genes'
rm -rf $output_dir/tile/vector-sdge
mkdir -p $output_dir/tile
singularity exec $CONTAINER ogr2ogr -f MVT $output_dir/tile/vector-sdge  \
$output_dir/vector/marker.gpkg \
-dsco MINZOOM=9 -dsco MAXZOOM=12 \
-dsco MAX_SIZE=2500000 -dsco MAX_FEATURES=1500000


echo 'convert factor'

python -m cart.factor \
-i $factor_result \
-o $output_dir/vector/factor.gpkg \
-x0 $x0 -s 80 -r 80

echo 'create vector tiles for factors'
rm -rf $output_dir/tile/vector-factor
singularity exec $CONTAINER ogr2ogr -f MVT $output_dir/tile/vector-factor  \
$output_dir/vector/factor.gpkg \
-dsco MINZOOM=9 -dsco MAXZOOM=12 \
-dsco MAX_SIZE=2500000 -dsco MAX_FEATURES=1500000


echo 'raster conversion'

mkdir -p $output_dir/raster
aws s3 cp $histology_path $output_dir/raster/histology.tif
singularity exec $CONTAINER gdal2tiles.py -z 6-15 \
$output_dir/raster/histology.tif $output_dir/tile/raster-histology

singularity exec $CONTAINER gdal_rasterize -a cnt_total -add -l all -tr 30 30 \
$output_dir/vector/full_sdge.fgb \
$output_dir/raster/count_sdge.tif

singularity exec $CONTAINER gdaldem hillshade -z 50 -compute_edges -alg Horn -igor \
  $output_dir/raster/count_sdge.tif $output_dir/raster/hillshade.tif

singularity exec $CONTAINER gdal2tiles.py -z 6-15 \
$output_dir/raster/hillshade.tif $output_dir/tile/raster-count

singularity exec $CONTAINER gdal_translate -of VRT -ot Byte -scale \
$output_dir/raster/count_sdge.tif $output_dir/interim/temp.vrt
singularity exec $CONTAINER gdal2tiles.py -z 6-15 \
$output_dir/interim/temp.vrt $output_dir/tile/raster-count

echo 'upload to S3'

aws s3 cp --recursive $output_dir/vector \
s3://$BUCKET/vector --profile default

aws s3 sync --metadata-directive REPLACE --content-encoding 'gzip' \
$output_dir/tile/vector-sdge s3://$BUCKET/tile/vector-sdge --profile default \
--exclude 'metadata.json'

echo 'upload vector tiles'

aws s3 cp $output_dir/tile/vector-sdge/metadata.json \
s3://$BUCKET/tile/vector-sdge/metadata.json \
--profile default

aws s3 sync --metadata-directive REPLACE --content-encoding 'gzip' \
$output_dir/tile/vector-factor s3://$BUCKET/tile/vector-factor --profile default \
--exclude 'metadata.json'

aws s3 cp $output_dir/tile/vector-factor/metadata.json \
s3://$BUCKET/tile/vector-factor/metadata.json \
--profile default

echo 'copy raster data'
aws s3 cp --recursive $output_dir/raster \
s3://$BUCKET/raster --profile default

echo 'upload raster tiles'

aws s3 sync \
$output_dir/tile/raster-histology s3://$BUCKET/tile/raster-histology \
--profile default

aws s3 sync \
$output_dir/tile/raster-count s3://$BUCKET/tile/raster-count \
--profile default

