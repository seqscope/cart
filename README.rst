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

```
$ ogr2ogr -f "GPKG"  -s_srs 'epsg:3857' -t_srs '+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=202000 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs' 2115t.gpkg  2115.gpkg
```

## metadata

false_easting = left tile's false_easting + left tiles (xmax-xmin) + gap
false_northing= below tile's false_northing + below tiles (ymax-ymin) + gap

gap is conveniently set to 20 

```
dataset: RD2-Liver-All
velocyto: True
tile_scheme:
  - 2213, 2214, 2215, 2216
  - 2113, 2114, 2115, 2116
marker_sets:
  - tiles: 2104, 2105, 2106, 2107
    topics:
      - zonation: Glul, Oat, Cyp2a5, Mup9, Mup17, Cyp2c29, Cyp2e1, Mup11, Hamp, Ass1, Serpina1e, Cyp2f2, Alb, Mup20
      - Macro: Cd5l, Cd74, Clec4f, H2-Ab1, C1qb, H2-Aa, C1qc, Csf1r, Ctss, Lyz2,
        tiles: 2104, 2105, 2106, 2107
      - ENDO: Aqp1, Dnase1l3, Gpr182, Gpihbp1, Kdr,
  - tiles: 2117, 2118
    topics:
      - Hep_Injured: Saa1, Saa2, Saa3
      - HPC: Spp1, Mmp7, Clu
      - Mp-Inflamed: Cd74, H2-Ab1, H2-Aa, H2-Eb1
      - Mp_Kupffer: Cbgl, Marco, Clec4f, C1qc, C1qb, Cfp, Fcna, Csf1r, C1qa
      - HSC-A: Col3a1, Col1a1, Col1a2, Mgp, Vwf, Col6a1, Adamtsl2, Gsn, Tagln, Acta2, Serpinh1, Timp1, Gja5, Bgn, Myl9, Fstl1, Tpm2, Col6a2, Flna, Col4a1, Sparc, Vim
tiles:
  - id: 2113
    extent:
      xmin: 2001
      ymin: 1145
      xmax: 100667
      ymax: 21392
    false_easting: -2001
    false_northing: -1145
  - id: 2114
    extent:
      xmin: 2001
      ymin: 1144
      xmax: 100667
      ymax: 21391
    false_easting: 1000687
    false_northing: 21412 

```
