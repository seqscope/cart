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

export DATASET=HD13-HLJNG-L1
export LANE=1
export CONTAINER=/home/yonghah/simg/gdal_alpine-normal-latest.sif
export sdge_dir=/gpfs/accounts/hmkang_root/hmkang0/shared_data/NGST-sDGEvelo/HD13-HLJNG-mouse
export marker_yaml=/home/yonghah/repo/cart/config/markers.yaml
export histology_path=s3://seqscope-hist2sdge/hd13-hljng-l1/referenced/histology.tif
export factor_result=/gpfs/accounts/hmkang_root/hmkang0/shared_data/tmp/LDA/HD13-HLJNG-mouse-new/analysis/LDA_hexagon.nFactor_10.d_12.lane_1.2101_2216.fit_result.tsv.gz
export factor_de=/gpfs/accounts/hmkang_root/hmkang0/shared_data/tmp/LDA/HD13-HLJNG-mouse-new/analysis/LDA_hexagon.nFactor_10.d_12.lane_1.2101_2216.DEgene.tsv.gz
export x0=-1580064 
export y0=-40438
export output_dir=/gpfs/accounts/hmkang_root/hmkang0/yonghah/HD13-HLJNG-L1
export BUCKET=hd13-hljng-l1


##################
# sDGE conversion
##################

echo 'metadata generation'

meta -n $DATASET -d $sdge_dir -o $output_dir/vector/metadata.yaml -l $LANE

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

echo 'upload to S3'

aws s3 cp $output_dir/vector/full_sdge.fgb  s3://$BUCKET/vector/full_sdge.fgb
aws s3 cp $output_dir/vector/marker.gpkg  s3://$BUCKET/vector/marker.gpkg
aws s3 cp $output_dir/vector/metadata.json  s3://$BUCKET/vector/metadata.json


echo 'create vector tiles for marker genes'
rm -rf $output_dir/tile/vector-sdge
mkdir -p $output_dir/tile
singularity exec $CONTAINER ogr2ogr -f MVT $output_dir/tile/vector-sdge  \
$output_dir/vector/marker.gpkg \
-dsco MINZOOM=9 -dsco MAXZOOM=12 \
-dsco MAX_SIZE=2500000 -dsco MAX_FEATURES=1500000

echo 'upload vector tiles'

aws s3 sync --metadata-directive REPLACE --content-encoding 'gzip' \
$output_dir/tile/vector-sdge s3://$BUCKET/tile/vector-sdge --profile default \
--exclude 'metadata.json'

aws s3 cp $output_dir/tile/vector-sdge/metadata.json \
s3://$BUCKET/tile/vector-sdge/metadata.json \
--profile default

echo 'sDGE count rasterization'

mkdir -p $output_dir/raster
singularity exec $CONTAINER gdal_rasterize -a cnt_total -add -l all -tr 30 30 \
$output_dir/vector/full_sdge.fgb \
$output_dir/raster/count_sdge.tif

singularity exec $CONTAINER gdaldem hillshade -z 50 -compute_edges -alg Horn -igor \
  $output_dir/raster/count_sdge.tif $output_dir/raster/hillshade.tif

aws s3 cp $output_dir/raster/count_sdge.tif  s3://$BUCKET/raster/count_sdge.tif
aws s3 cp $output_dir/raster/hillshade.tif  s3://$BUCKET/raster/hillshade.tif

echo 'tiling count raster'
singularity exec $CONTAINER gdal2tiles.py -z 6-15 \
$output_dir/raster/hillshade.tif $output_dir/tile/raster-count

aws s3 sync \
$output_dir/tile/raster-count s3://$BUCKET/tile/raster-count \
--profile default


#################
# Factor conversion
#################

echo 'convert factor'

python -m cart.factor \
-i $factor_result \
-o $output_dir/vector/factor.gpkg \
-x0 $x0 -y0 $y0 -s 80 -r 80

aws s3 cp $output_dir/vector/factor.gpkg  s3://$BUCKET/vector/factor.gpkg
aws s3 cp $factor_result  s3://$BUCKET/interim/factor/result.tsv.gz
aws s3 cp $factor_de s3://$BUCKET/interim/factor/de.tsv.gz

echo 'create vector tiles for factors'
rm -rf $output_dir/tile/vector-factor
singularity exec $CONTAINER ogr2ogr -f MVT $output_dir/tile/vector-factor  \
$output_dir/vector/factor.gpkg \
-dsco MINZOOM=9 -dsco MAXZOOM=12 \
-dsco MAX_SIZE=2500000 -dsco MAX_FEATURES=1500000

aws s3 sync --metadata-directive REPLACE --content-encoding 'gzip' \
$output_dir/tile/vector-factor s3://$BUCKET/tile/vector-factor --profile default \
--exclude 'metadata.json'

aws s3 cp $output_dir/tile/vector-factor/metadata.json \
s3://$BUCKET/tile/vector-factor/metadata.json \
--profile default


##################
# histology tiling 
##################

echo 'raster conversion'

aws s3 cp $histology_path $output_dir/raster/histology.tif
singularity exec $CONTAINER gdal2tiles.py -z 6-15 \
$output_dir/raster/histology.tif $output_dir/tile/raster-histology

echo 'copy raster data'
aws s3 cp $output_dir/raster/histology.tif  s3://$BUCKET/raster/histology.tif

echo 'upload raster tiles'
aws s3 sync \
$output_dir/tile/raster-histology s3://$BUCKET/tile/raster-histology \
--profile default

