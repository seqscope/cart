""" This module is used for generating metadata yaml for dataset"""

import argparse
from pathlib import Path

import yaml
import pandas as pd

from .util import read_barcodes


def main():
    '''
    run script for generating metadata
    '''
    parser = argparse.ArgumentParser(
        description="Create metadata for Seq-Scope dataset")
    parser.add_argument(
        "-n", "--name", type=str, required=True,
        help="dataset name. e.g. RD2-Liver-All")
    parser.add_argument(
        "-d", "--data-dir", type=str, required=True,
        help="Input (STTools output) directory")
    parser.add_argument(
        "-o", "--output", type=str, default="metadata.yaml",
        help="Output file name")
    parser.add_argument(
        "-l", "--layout", type=str, default="hiseq",
        help="tile layout")
    parser.add_argument(
        "-g", "--gap", type=int, default=0,
        help="tile layout")
    args = parser.parse_args()

    metadata = {
        'dataset': args.name,
        'data_dir': args.data_dir,
        'tiles': [],
    }
    layout = read_layout(args.layout)
    tiles = extract_metadata_tiles(args.data_dir, layout)
    Tile.grid_width, Tile.grid_height = identify_tile_size(tiles)
    Tile.grid_gap = args.gap
    Tile.max_row = int(layout['row'].max())
    print(f"Grid width: {Tile.grid_width}, height: {Tile.grid_height}")
    
    for _, tile in tiles.items():
        tile.set_false_origin()

    # required for pyyaml tag issue
    tile_dict = {key:tile.__dict__ for key, tile in tiles.items()}

    metadata['tiles'] = tile_dict 
    metadata['number_of_tiles'] = len(metadata['tiles']) 
    metadata['list_of_tiles'] = sorted(list(tile_dict.keys())) 
    metadata['tile_layout'] = {
        'scheme': args.layout,
        'max_row': Tile.max_row,
        'grid_gap': Tile.grid_gap,
        'grid_width': Tile.grid_width,
        'grid_height': Tile.grid_height
    }
    with open(args.output, 'w') as file:
        yaml.dump(metadata, file)


def identify_tile_size(tiles):
    ''' 
    infer tile width and height
    width = max(xmax-xmin)
    height = max(ymax-ymin) '''

    width_max = 0
    height_max = 0

    for _, tile in tiles.items():
        width = tile.xmax - tile.xmin
        height = tile.ymax - tile.ymin
        if width > width_max: 
            width_max = width 
        if  height > height_max: 
            height_max = height 
        
    return width_max, height_max


def extract_metadata_tiles(data_root, layout):
    ''' loop over data dir and append metadat for each tile'''
    metadata_tiles = {} 
    for lane in Path(data_root).iterdir():
        if lane.is_dir():
            for tile in lane.iterdir():
                if tile.is_dir():
                    metadata_tiles[f"{lane.stem}-{tile.stem}"] =\
                        _metadata_tile(lane, tile, layout)
    return metadata_tiles


def _metadata_tile(lane, tile, layout):
    tile = Tile(int(lane.stem), int(tile.stem), str(tile))
    tile.get_rowcol(layout)
    tile.get_extent()
    return tile


def read_layout(layout='hiseq'):
    ''' read layout tsv file which contains row/col info'''
    layout_table = ''
    if layout=='hiseq':
        layout_table = 'config/hiseq_layout.tsv'
    return pd.read_csv(layout_table, sep='\t').set_index(['lane', 'tile'])  # type: ignore


class Tile:
    ''' class for tile metadata'''
    grid_gap = 0
    grid_width = 0
    grid_height = 0 
    max_row = 0

    def __init__(self, lane_id, tile_id, data_dir):
        self.lane_id = lane_id
        self.tile_id = tile_id
        self.data_dir = data_dir

        self.row = 0 
        self.col = 0 
        self.false_easting = None
        self.false_northing = None

        self.xmin: int = 0
        self.ymin: int = 0
        self.xmax: int = 0
        self.ymax: int = 0


    def get_rowcol(self, layout):
        """ get row/col of a tile"""
        self.row = int(layout.loc[(self.lane_id, self.tile_id)].row)
        self.col = int(layout.loc[(self.lane_id, self.tile_id)].col)


    def set_false_origin(self):
        '''
        location of local origin compared to global origin
        global origin is set to the tile at (max_row, 1)'s local origin
        '''
        self.false_easting = -int((Tile.grid_width + Tile.grid_gap) * (self.col - 1))
        self.false_northing = -int(
            (Tile.grid_height + Tile.grid_gap) * \
            (Tile.max_row - self.row )
        )


    def get_extent(
        self, barcode_file = 'barcodes.tsv.gz',
        x='x', y='y'):  # pylint: disable=invalid-name

        """ get extent of a tile"""
        df_barcodes = read_barcodes(Path(self.data_dir) / barcode_file )
        desc = df_barcodes[[x, y]].describe(percentiles=None)
        self.xmin = int(desc['x']['min'])
        self.ymin = int(desc['y']['min'])
        self.xmax = int(desc['x']['max'])
        self.ymax = int(desc['y']['max'])


if __name__=='__main__':
    main()
