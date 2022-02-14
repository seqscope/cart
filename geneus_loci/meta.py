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
    args = parser.parse_args()

    metadata = {
        'dataset': args.name,
        'data_dir': args.data_dir,
        'tiles': [],
    }
    layout = read_layout(args.layout)
    metadata['tiles'] = metadata_tiles(args.data_dir, layout)
    metadata['number_of_tiles'] = len(metadata['tiles']) 
    metadata['list_of_tiles'] = sorted(list(metadata['tiles'].keys())) 
    metadata['tile_layout'] = {
        'scheme': args.layout,
        'grid_gap': Tile.grid_gap,
        'grid_width': Tile.grid_width,
        'grid_height': Tile.grid_height
    }
    with open(args.output, 'w') as file:
        yaml.dump(metadata, file)


def metadata_tiles(data_root, layout):
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
    tile.set_rowcol(layout)
    tile.set_extent()
    return tile.__dict__


def read_layout(layout='hiseq'):
    ''' read layout tsv file which contains row/col info'''
    layout_table = ''
    if layout=='hiseq':
        layout_table = 'geneus_loci/hiseq_layout.tsv'
    return pd.read_csv(layout_table, sep='\t').set_index(['lane', 'tile'])  # type: ignore


class Tile:
    ''' class for tile metadata'''
    grid_gap = 20
    grid_width = 98666
    grid_height = 20248

    def __init__(self, lane_id, tile_id, data_dir):
        self.lane_id = lane_id
        self.tile_id = tile_id
        self.data_dir = data_dir

        self.row = None
        self.col = None
        self.false_easting = None
        self.false_northing = None

        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0


    def set_rowcol(self, layout):
        """ get row/col of a tile"""
        self.row = int(layout.loc[(self.lane_id, self.tile_id)].row)
        self.col = int(layout.loc[(self.lane_id, self.tile_id)].col)
        self.false_easting = -int((Tile.grid_width + Tile.grid_gap) * self.col)
        self.false_northing = int((Tile.grid_height + Tile.grid_gap) * self.row)


    def set_extent(
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
