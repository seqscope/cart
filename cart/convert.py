# type: ignore
import argparse
import os
from pathlib import Path
import pandas as pd
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
    ''' 
    $ python -m cart.convert \
    -i ~/data/seqscope/HD31-HMKYV-human-L2/sge \
    -o ~/data/seqscope/HD31-HMKYV-human-L2/output/vector/test.tsv.gz
    '''
    parser = argparse.ArgumentParser(description="Convert SeqScope data to geographic format")
    parser.add_argument("-o", "--out", type=str, required=True, help="Output file")
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help="input data dir")
    args = parser.parse_args()
    output_path = Path(args.out)
    output_path.parents[0].mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.input)
    features = data_dir / "features.tsv.gz"
    barcodes = data_dir / "barcodes.tsv.gz"
    manifest = data_dir / "manifest.tsv"
    matrix   = data_dir / "matrix.mtx.gz"
    print(args) 
    convert(
        barcodes,
        matrix,
        features,
        manifest,
        output_path
    )

    # convert(args.input, args.out)


def convert(
    barcode_path, 
    matrix_path, 
    feature_path, 
    manifest_path, 
    output_path):
    
    ''' 
    read three tables and the matching manifest; 
    join and add global coordinates; 
    then save the joined output as tsv.gz
    ''' 
    
    # read barcodes
    df_b = pd.read_csv(
        barcode_path, 
        sep="\t",
        names=[
            'barcode', 'barcode_id', 'col1', 
            'lane', 'tile',
            'y_', 'x_', 'counts'],
        dtype = {
            'barcode': str,
            'barcode_id': 'int',
            'y_': 'int32',
            'x_': 'int32',
        }
    )
    
    # read manifest
    manifest = pd.read_csv(manifest_path, sep="\t").set_index('id')  
    manifest['width'] = manifest['ymax'] - manifest['ymin']
    manifest['height'] = manifest['xmax'] - manifest['xmin']
    grid_width = manifest.width.max()    # tile grid width
    grid_height = manifest.height.max()  # tile grid height
    
    # add global coordinates
    df_b = lc2gc(df_b, grid_width, grid_height, manifest)
    
    # read matrix 
    df_m = pd.read_csv(matrix_path, sep=" ", skiprows=3,
        names = [
            'gene_id', 'barcode_id', 
            'Gene', 'GeneFull', 
            'VelocytoSpliced', 'VelocytoUnspliced', 
            'VelocytoAmbiguous'],
        dtype= {
            'gene_id': 'int32',
            'barcode_id': 'int',
            'Gene': 'int8',
            'GeneFull': 'int8',
            'VelocytoSpliced': 'int8', 
            'VelocytoUnspliced': 'int8',
            'VelocytoAmbiguous': 'int8'
        }
    )
    
    # read gene table
    df_g = pd.read_csv(feature_path, sep="\t",
        names = ['name', 'gene_name', 'gene_id',  'counts'],
        dtype = {
            'name': str,
            'gene_name': str,
            'gene_id': 'int32',
            'counts': str
        }
    ).set_index('gene_id')[['gene_name']]
    
    # join coords and gene_name to matrix
    df_merged = (df_m
        .merge(df_b, on='barcode_id')
        .merge(df_g, on='gene_id')
    ).drop(['gene_id', 'barcode_id'], axis=1)
    
    # add total count
    df_merged['cnt_total'] =  \
        df_merged['Gene'] +\
        df_merged['GeneFull'] +\
        df_merged['VelocytoSpliced'] +\
        df_merged['VelocytoUnspliced'] +\
        df_merged['VelocytoAmbiguous']
    
    # save output
    df_merged.to_csv(
        output_path, 
        sep="\t", 
        index=False,
        compression='gzip'
    )
    print(f"Table with {len(df_merged)} rows saved at {output_path}")
    
    # for future use
    return df_merged


def lc2gc(df, grid_width, grid_height, manifest):
    ''' 
    add global coordinates to barcode dataframe 
    '''
    um_to_sge = 26.67 
    p = df['tile'] // 1000                 # first digit of tile number 
    q = (df['tile']  - p  * 1000) // 100   # second digit
    k = df['tile'] - p * 1000 - q * 100    # last two digits
    df['m'] = (p - 1) * 16 + k             # row number of tile from the bottom
    df['n'] = 2 * (2- df['lane']) + q      # col number of tile from the left
    
    # add xmin, ymin of a tile from manifest
    df = df.assign(
        tile_id=df.lane.map(str) + "_" + df.tile.map(str)
    ).set_index('tile_id')
    df = df.join(manifest[['xmin', 'ymin']])
    
    # global coords
    df['x'] = (df.x_ + grid_width  * (df.m-1) - df.ymin) / um_to_sge  # note that xmin, ymin came from manifest
    df['y'] = (df.y_ + grid_height * (df.n-1) - df.xmin ) / um_to_sge  # where x, y flipped
    
    df = df[['barcode_id',  'x', 'y']].set_index('barcode_id')
    return df


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


def convert2gpkg(matrix, barcodes, features, output: str, t_srs: str, driver='GPKG'):
    '''convert dataset to gpkg or fgb'''
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
