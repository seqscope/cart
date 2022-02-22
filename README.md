## set up

[Poetry](https://python-poetry.org/) helps setting up virtual env and installation.

```
$ module load python/3.9.1 gdal
$ poetry shell
$ poetry install
$ meta
```


## metadata generation

```
meta -d /data/dir/ -o metadata.yaml -n DATASET_NAME -g 15
```

* false_easting = -max(tile width) * (col - 1) + gap
* false_northing=  max(tile height)* (max_row - col) + gap

false_easting or northing dictates where the world coordinate systems origin is located at ccompared to local coordinate system.


## convert to geospatial format 

converts all tiles to geospatial format with correct CRS

```
convert -d /data/dir -o /output/dir -m /path/to/metadata.yaml --cpu=4 
```

merge all tiles to one single geospatial file's one merged layer named 'all'. Since gdal module in greatlakes doesn't have ogrmerge.py, we need to use gdal container.

```
$ module load singularity
$ singularity pull docker://osgeo/gdal:alpine-normal-latest
$ find data/geospatial -type f -print0 | xargs -r0 singularity exec gdalimage.simg ogrmerge.py -o data/geospatial/merged.gpkg -f GPKG -progress -single -nln all   
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
`
Create a hillshade

```
gdaldem hillshade -z 50 -compute_edges -alg Horn \
-combined \   
merged-tr30.tif hillshade-horn.tif 
```
use -igor instead of -combined for lighter relief

## Misc notes

``

generate vector tiles with tippecanoe

```
$ tippecanoe  -o vectortile.mbtiles -z14 -Z9  -pd  -M 2000000 -O 1000000 input.geojson -s EPSG:3857
```



