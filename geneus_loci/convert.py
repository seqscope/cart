import io
import argparse
from pathlib import Path

import pandas as pd
import geopandas as gpd


def main():
    parser = argparse.ArgumentParser(description="Visualize tiles for SeqScope data")
    parser.add_argument(
        "-d", "--in-dir", type=str, required=True, 
        help="Input (STTools output) directory")
    parser.add_argument(
        "-o", "--out", type=str, required=True, 
        help="Output gpkg file path")
    parser.add_argument(
        "-l", "--layer", type=str, default="default", 
        help="Output file layer")
    parser.add_argument(
        "-f", "--format", type=str, default="FlatGeobuf", 
        help="Output file format")
    args = parser.parse_args()
    data_dir = Path(args.in_dir)
    features = data_dir / "features.tsv"
    barcodes = data_dir / "barcodes.tsv"
    matrix   = data_dir / "data"
    
    convert2gpkg(matrix, barcodes, features, output=args.out, layer=args.layer)


def read_features(features) -> pd.DataFrame:
    header = ['name', 'short_name', 'desc', 'gene_id', 'total_count', 'counts']
    df = pd.read_csv(features, sep="\t", names=header).set_index("gene_id")
    return df 


def read_barcodes(barcodes) -> pd.DataFrame:
    header = [
        'barcode', 'barcode_id', 'col1', 'col2', 'lane', 'tile', 
        'y', 'x', 'counts']
    df = pd.read_csv(barcodes, sep="\t", names=header).set_index('barcode_id')
    return df


def read_matrix(matrix) -> pd.DataFrame:
    header = ['gene_id', 'barcode_id', 'cnt_spliced', 'cnt_unspliced', 'cnt_ambiguous']
    df = pd.read_csv(matrix, sep=" ", names=header, skiprows=3)
    return df


def matrix2widegdf(matrix, barcodes) -> gpd.GeoDataFrame:
    '''convert matrix to wide geodataframe with xy info from barcode table
    not used now
    '''
    df_matrix_long = read_matrix(matrix)
    df_matrix_wide = (
        df_matrix_long.groupby(
            ['barcode_id', 'gene_id'])[['cnt_spliced', 'cnt_unspliced', 'cnt_ambiguous']]
        .sum()
        .unstack('gene_id', fill_value=0)
    )
    df_matrix_wide.columns = [
        f"g{t[1]}_{t[0]}" for t in df_matrix_wide.columns.to_flat_index()]
    df_barcode = read_barcodes(barcodes)[['x', 'y']]
    df = df_barcode.merge(df_matrix_wide, on='barcode_id')
    gdf = (gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
        .drop(['x', 'y'], axis=1)
        .set_crs('epsg:3857')
    )
    return gdf


def matrix2gdf(matrix, barcodes, features) -> gpd.GeoDataFrame:
    '''convert matrix to long geodataframe with xy info from barcode table'''
    df_matrix = read_matrix(matrix)
    df_feature = read_features(features)[['short_name']]
    df_barcode = read_barcodes(barcodes)[['x', 'y']]
    df = (df_barcode
        .merge(df_matrix, on='barcode_id')
        .merge(df_feature, on='gene_id')
    )
    gdf = (gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
        .drop(['x', 'y'], axis=1)
        .set_crs('epsg:3857')
    )
    return gdf


def convert2gpkg(matrix, barcodes, features, output: str, layer:str='default', format:str='FlatGeobuf'):
    '''convert dataset to gpkg'''
    gdf = matrix2gdf(matrix, barcodes, features) 
    gdf.to_file(output, layer=layer, driver=format)


if __name__ == '__main__':
    main()