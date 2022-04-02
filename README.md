# Cart

tools for CartoSeq including metatdata generation, file converstion, and raster plotting.

## set up

```
pip install "git+https://github.com/seqscope/cart.git@v0.1.2"
```

### for developers
[Poetry](https://python-poetry.org/) helps setting up virtual env and installation.

```
$ module load python/3.9.1 gdal
$ poetry shell
$ poetry install
$ meta
```

## coordinate conversion
from sDGE to GCS (Global Coordinate System)
```
>>> from cart import meta
>>> w, h = meta.identify_tile_size("/gpfs/accounts/hmkang_root/hmkang0/shared_data/NGST-sDGE/HD30-inj-colon-comb", 2)
>>> meta.sdge_to_gcs(1, 1112, 123, 456, width=w, height=h)
(1086362, 41054)
>>>
```

## metadata generation

```
meta -d /data/dir/ -o metadata.yaml -n DATASET_NAME -g 15
```

* false_easting = -max(tile width) * (col - 1) + gap
* false_northing=  max(tile height)* (max_row - col) + gap

false_easting or northing dictates where the world coordinate systems origin is located at ccompared to local coordinate system.


## convert to geospatial format 


### piecewise conversion

converts all tiles to geospatial format with correct CRS

```
convert -d /data/dir -o /output/dir -m /path/to/metadata.yaml --cpu=4 
```

### merge tiles

merge converted geopatial files per tile into one single geospatial file (layer name 'all'). We need to use gdal container since gdal module in greatlakes doesn't have ogrmerge.py strangely.

```
$ module load singularity
$ singularity pull docker://osgeo/gdal:alpine-normal-latest
$ find data/geospatial -type f -print0 | xargs -r0 singularity exec gdalimage.simg ogrmerge.py -o data/geospatial/merged.gpkg -f GPKG -progress -single -nln all   
```

### filter dataset with markers

```
$ filter -i merged.gpkg -o filtered.gpkg -m markers.yaml -n DATASET_NAME_IN_MARKER_YAML
```


## generate a raster image

Create a raster for total count
```
gdal_rasterize -a cnt_total -add -l all -tr 30 30  merged.gpkg merged-tr30.tif
```
* tr 30 30 means 1 pixel = 30 unit

create tiff with selected genes
```
gdal_rasterize -a cnt_total -add -l all -tr 200 200 -where "gene_name in ('Hbb-bs','Hba-a1','Hba-a2')" merged.gpkg Hep_RBC-tr200.tiff
```

Create a hillshade

```
gdaldem hillshade -z 50 -compute_edges -alg Horn \
-combined \   
merged-tr30.tif hillshade-horn.tif 
```
use -igor instead of -combined for lighter relief

## Misc notes


generate vector tiles with tippecanoe
```
$ tippecanoe  -o vectortile.mbtiles -z14 -Z9  -pd  -M 2000000 -O 1000000 input.geojson -s EPSG:3857
```

Merge TIFF files with gdal_merge.py in GDAL package
```
find *_modified.tif -print0 | xargs -r0 gdal_merge.py -o histology.tif 
```

Create image tile pyramid with gdal2tile in GDAL package (zoom range between 6-15)
```
 gdal2tiles.py -z 6-15 --processes=8 histology.tif tile-histology
```
