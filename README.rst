set up
```
$ poetry shell
```


convert matrix to FlatGeobuf and GeoJSON

```
$ python geneus_loci/convert.py -d /home/yongha/scratch/st/2/2113 -o data/test.fgb -f FlatGeobuf
$ ogr2ogr -f GeoJSON liver.geojson test.fgb -progress
```

generate vector tiles
```
$ tippecanoe  -o tip-o1m.mbtiles -z14 -Z9  -pd  -M 2000000 -O 1000000 liver.geojson -s EPSG:3857
```