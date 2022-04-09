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

export DATASET=HD30-HML22-InCol
export sdge_dir=/path/to/sdge
export marker_yaml = /path/to/marker.yaml
export histology_path=/path/to/histology/file
export factor_result=/path/to/factor/file
export x0=-1579984
export output_dir=/path/to/output

echo 'metadata generation'

cart.meta -n $DATASET -d /data/dir -o $output_dir/vector/metadata.yaml -l 2

echo 'convert sDGE'

cart.convert -o $output_dir/interim/vector-sdge \
-m $output_dir/vector/metadata/yaml -c 1

find $output_dir/interim/vector-sdge -type f -print0 \
| xargs -r0 singularity exec $CONTAINER ogrmerge.py \
-o $output_dir/vector/full_sdge.fgb -f FlatGeobuf -single -nln all

cart.filter -i $output_dir/vector/full_sdge.fgb \
-o $output_dir/vector/marker.fgb -m $marker_yaml -n $DATASET

$CONTAINER ogr2ogr -f MVT $output_dir/tile/vector-sdge  \
$output_dir/vector/marker.fgb \
-dsco MINZOOM=9 -dsco MAXZOOM=12 \
-dsco MAX_SIZE=2500000 -dsco MAX_FEATURES=1500000

echo 'convert factor'

cart.factor \
-i $factor_result \
-o $output_dir/vector/factor_hexagon.fgb \
-x0 $x0 -s 80 -r 80

echo 'raster conversion'

gdal_rasterize -a cnt_total -add -l all -tr 30 30 \
$output_dir/vector/full_sdge.fgb \
$output_dir/raster/count_sdge.tif

gdal2tiles.py -z 6-15 --processes=8 \
$histology_path $output_dir/tile/raster-histology

gdal2tiles.py -z 6-15 --processes=8 \
$outpu_dir/raster/count_sdge.tif $output_dir/tile/raster-count

echo 'upload to S3'

aws s3 cp --recursive $output_dir/vector \
s3://$DATASET/vector --profile sqs

aws s3 sync --metadata-directive REPLACE --content-encoding 'gzip' \
$output_dir/tile/vector-sdge s3://$DATASET/tile/vector-sdge --profile sqs \
--exclude 'metadata.json'

aws s3 cp $output_dir/tile/vector-sdge/metadata.json \
s3://$DATASET/tile/vector-sdge/metadata.json \
--profile sqs

aws s3 sync \
$output_dir/tile/raster-histology s3://$DATASET/tile/raster-histology \
--profile sqs 

aws s3 sync \
$output_dir/tile/raster-count s3://$DATASET/tile/raster-count \
--profile sqs

