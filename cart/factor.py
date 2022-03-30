import argparse
import math
from pathlib import Path

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon


def main():
    """
    run script for converting factor data to geospatial hexgagon format
    ```
    $ python -m cart.factor -i input.tsv.gz -o output.gpkg -s 80 -r 80
    ````
    """
    parser = argparse.ArgumentParser(
        description="Converting factorization result to hexgagon file")
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help="Input tsv or tsv.gz file path")
    parser.add_argument(
        "-o", "--output", type=str, default="output.gpkg",
        help="Output file name")
    parser.add_argument(
        "-x0", "--false-easting", type=int, default=0,
        help="false easting")
    parser.add_argument(
        "-y0", "--false-northing", type=int, default=0,
        help="false northing")
    parser.add_argument(
        "-s", "--scale", type=int, default=80,
        help="scale multiplied to original xy")
    parser.add_argument(
        "-r", "--radius", type=int, default=80,
        help="inner radius of hexagon")
    parser.add_argument(
        "-a", "--angle", type=int, default=0,
        help="rotation angle of hexagon")
    args = parser.parse_args()

    # data_dir = "/Users/yonghah/data/seqscope/hd30-hml22-incol/lda"
    # fit_result = "LDA_hexagon.nFactor_10.d_18.lane_2.2112_2113_2212_2213.fit_result.tsv" 
    # tsv_path = Path(data_dir) / fit_result
    # false_easting = -2666223
    # false_northing = 0
    # scale = 80
    # radius = 80  # inner radius of hexagon
    
    df = read_centroid(
        args.input, 
        false_easting=args.false_easting, 
        false_northing=args.false_northing,
        scale=args.scale
    )
    gdf = xy_to_hexagon(df, args.radius, args.angle)
    gdf.to_file(args.output)


def xy_to_hexagon(df, inner_radius, rotation=0):
    """
    convert pandas dataframe with x,y centroid 
    to geodataframe with hexagons 
    """
    side = inner_radius * 2 / math.sqrt(3) 
    df['geometry'] = df.apply(
        lambda row: create_hexagon(side, row.x, row.y, rotation), 
        axis=1)
    gdf = gpd.GeoDataFrame(
        df, geometry=df['geometry']
    ).set_crs('EPSG:3857')
    return gdf


def read_centroid(
        tsv_path, 
        x_col = 'Hex_center_y',
        y_col = 'Hex_center_x',
        false_easting=0, 
        false_northing=0, 
        scale=80):
    """ read centroid tsv and convert it to dataframe
    and adjust scale and origin
    """
    df = pd.DataFrame(pd.read_csv(tsv_path, sep="\t"))  # to handle type error warning   
    df['x'] = df[x_col] * scale - false_easting 
    df['y'] = df[y_col] * scale - false_northing 
    df = df.drop([
        'Hex_center_x', 'Hex_center_y', 
        'offs_x', 'offs_y',
        'hex_x', 'hex_y'
    ], axis=1)
    return df 


def create_hexagon(r, x, y, rotation=0):
    """
    Create a hexagon centered on (x, y), side-topped when rotation=0 
    :param r: length of the hexagon's edge
    :param x: x-coordinate of the hexagon's center
    :param y: y-coordinate of the hexagon's center
    :return: The polygon containing the hexagon's coordinates
    """
    c = [[
        x + math.cos(math.radians(angle + rotation)) * r, 
        y + math.sin(math.radians(angle + rotation)) * r
    ] for angle in range(0, 360, 60)]
    return Polygon(c)


if __name__=='__main__':
    main()
