import argparse
import os
from pathlib import Path
from multiprocessing import Pool
import subprocess

import yaml
import geopandas as gpd

# from osgeo import gdal


from .util import (
    read_matrix,
    read_features,
    read_barcodes
)

def main():
    parser = argparse.ArgumentParser(description="Convert SeqScope data to geographic format")
    parser.add_argument(
        "-o", "--out", type=str, required=True,
        help="Output dir")
    parser.add_argument(
        "-m", "--meta", type=str, default='metadata.yaml',
        help="Output dir")
    parser.add_argument(
        "-c", "--cpu", type=int, default=6,
        help="number of processes") 
    args = parser.parse_args()
    with open(args.meta) as f:
        metadata = yaml.safe_load(f)  
    tiles = list(metadata['tiles'].keys())
    args_list = map(lambda t: (t, args.out, metadata),tiles)
    
    with Pool(args.cpu) as p:
        p.starmap(convert_single, args_list)


def convert_single(lt_id, outdir, metadata):
    '''read metadata.yaml from data root and convert a single tile'''
    # create outdir if not exist
    Path(outdir).mkdir(parents=True, exist_ok=True)

    # prepare data files 
    metadata_tile = metadata['tiles'][lt_id]
    data_dir = Path(metadata_tile['data_dir'])
    features = data_dir / "features.tsv.gz"
    barcodes = data_dir / "barcodes.tsv.gz"
    matrix   = data_dir / "matrix.mtx.gz"
    t_srs = shifted_srs(
            metadata_tile['false_easting'], 
            metadata_tile['false_northing'])
    output_path = str(Path(outdir) / f"{lt_id}.gpkg")
    print(f"output_path:{output_path}")
    convert2gpkg(
        matrix, barcodes, features,
        output=output_path,
        t_srs=t_srs)


def convert2gpkg(matrix, barcodes, features, output: str, t_srs: str):
    '''convert dataset to gpkg'''
    gdf = matrix2gdf(matrix, barcodes, features, t_srs)
    gdf = gdf.drop(['barcode_id', 'gene_id'], axis=1)
    schema = gpd.io.file.infer_schema(gdf)  # type: ignore
    int32_fields = ['cnt_spliced', 'cnt_unspliced', 'cnt_ambiguous']
    for f in int32_fields:
        schema['properties'][f] = 'int32'
    # gdf.to_file(output, layer=layer, driver=format, schema=schema, index=False)
    gdf = gdf.to_crs('epsg:3857')  # type:ignore
    gdf.to_file(output, layer='all', driver='GPKG', schema=schema, index=False)
    print(f"conversion finisehd at {output}")


def matrix2gdf(matrix, barcodes, features, t_srs="epsg:3857") -> gpd.GeoDataFrame:
    '''convert matrix to long geodataframe with xy info from barcode table'''
    df_matrix = read_matrix(matrix)
    df_feature = read_features(features)[['gene_name']]
    df_barcode = read_barcodes(barcodes)[['x', 'y']]
    df = (df_barcode
        .merge(df_matrix, on='barcode_id')
        .merge(df_feature, on='gene_id')
    )
    gdf = (gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
        .drop(['x', 'y'], axis=1)
        .set_crs(t_srs)  # type: ignore
    )
    print(gdf.dtypes)
    return gdf


def shifted_srs(false_easting, false_northing):
    '''shifted srs for epsg:3857'''
    proj =  '+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 ' +\
            f'+x_0={false_easting} +y_0={false_northing} ' +\
            '+k=1 +units=m +nadgrids=@null +wktext +no_defs'
    return proj


def filter():
    '''filter merged dataset with marker list'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help="Input geo file")
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help="Output filtered file")
    parser.add_argument(
        "-m", "--marker", type=str, required=True,
        help="marker set configuration")
    parser.add_argument(
        "-n", "--dataset-name", type=str, required=True,
        help="marker set configuration")
    parser.add_argument(
        "-s", "--singularity", type=str, default=None,
        help="singularity image")
    args = parser.parse_args() 

    with open(args.marker) as f:
        config = yaml.safe_load(f)
    if os.path.exists(args.output):
        os.remove(args.output)
    for name, items in config['marker_sets'][args.dataset_name].items():
        option = make_trans_options(name, items, args.singularity)
        create_layer(args.input, args.output, option)


def make_trans_options(layername, filter_items, singularity):
    in_clause = construct_in_clause(filter_items)
    trans_options = {
        "format":'GPKG',
        "layerName": layername,
        "accessMode": 'append',
        "where": f"gene_name in ({in_clause})",
        "singularity": singularity 
    }
    return trans_options


def create_layer(input, output, trans_options):
    '''
    ogr2ogr filtred.gpkg  merged.gpkg \
    -f GPKG -append -nln test \
    -where "gene_name in ('Mup3', 'Apoa2', 'Apoc3')"
    '''
    executor = 'ogr2ogr'
    if trans_options['singularity']:
        executor = f"singularity exec {trans_options['singularity']} ogr2ogr"
    command = f"{executor} " +\
        f"{output} {input} -f {trans_options['format']} " +\
        f"-append -update -nln {trans_options['layerName']} " +\
        f"-where \"{trans_options['where']}\""
    print(command)
    subprocess.call([command], shell=True)


def construct_in_clause(items):
    item_list = [i.strip() for i in items.split(',')]
    return "'" + "','".join(item_list) + "'"


if __name__ == '__main__':
    main()
