import io
import json
from pathlib import Path
import math
from cart import factorde

import pytest
import pandas as pd
import numpy as np
import geopandas as gpd

from cart import (
    __version__,
)
from cart.convert import (
    matrix2gdf,
    read_barcodes,
    read_features,
    read_matrix,
)
from cart.util import (
    read_barcodes,
    read_features,
    read_matrix,
)
from cart.meta import (
    # get_extent,
    read_layout,
)
from cart.split import (
    _extract_genes
)
from cart.factor import (
    read_centroid,
    create_hexagon
)
from cart.factorde import (
    _conversion,
)

@pytest.fixture
def features():
    tsv_string = \
        "ENSMUSG00000064842	Gm26206	Gene Expression	1	0	0,0,0" + "\n" + \
        "ENSMUSG00000051951	Xkr4	Gene Expression	2	83	3,80,0" + "\n" + \
        "ENSMUSG00000025900	Rp1	Gene Expression	3	5	0,5,0"
    return io.StringIO(tsv_string)


@pytest.fixture
def barcodes():
    tsv_string = \
        "AAAAAGTGTGGCTCGGATAAGAGTGAGAAG	1	7182	1	2	2113	1	1	1,0,0" + "\n" + \
        "AAAACAAAAAAGCACTACCGGTTAAGCAGC	2	7501	2	2	2113	1	2	2,0,0" + "\n" + \
        "AAAACAAAAACCAATTTGAGGTGGTAGCGC	3	7693	2	2	2113	1	3	2,0,0" + "\n" + \
        "AAAACAAAAACGGTATCATTCCTGTGGGTA	4	7789	2	2	2113	1	4	0,2,0" + "\n" + \
        "AAAACAAAAAGATAATAAACGACATTCGTC	5	7893	4	2	2113	2	1	4,0,0" + "\n" + \
        "AAAACAAAAAGCCAGATATAGCTGCTGAGG	6	7962	6	2	2113	2	2	6,0,0" + "\n" + \
        "AAAACAAAAATAGCATCAATGGTAGAAGTC	7	8219	6	2	2113	2	3	6,0,0" + "\n" + \
        "AAAACAAAAATCATATAATAGATAGCATTC	8	8337	2	2	2113	2	4	2,0,0" + "\n" + \
        "AAAACAAAACAGCCCTAATTGATATCCATA	9	8802	1	2	2113	3	1	1,0,0" + "\n" + \
        "AAAACAAAACCAATATCAGCCAGATGCATT	10	8874	3	2	2113	3	2	3,0,0" + "\n" + \
        "AAAACAAAACCGCGAATATCCTGCAAATCG	11	8985	2	2	2113	3	3	2,0,0" + "\n" + \
        "AAAACAAAACGAAGAGAAGCGCAAGTAGAA	12	9017	10	2	2113	3	4	9,0,1"
    return io.StringIO(tsv_string)


@pytest.fixture
def matrix():
    mat_string = \
        "%%MatrixMarket matrix coordinate integer general" + "\n" + \
        "%" + "\n" + \
        "2 5 7" + "\n" + \
        "1 1 1 0 0" + "\n" + \
        "1 2 2 0 0" + "\n" + \
        "1 3 1 0 0" + "\n" + \
        "1 12 1 0 0" + "\n" + \
        "2 3 1 0 0" + "\n" + \
        "2 4 0 2 0" + "\n" + \
        "2 5 1 0 0" + "\n" + \
        "2 6 1 0 0" 
    return io.StringIO(mat_string)


def test_read_features(features):
    df = read_features(features)
    assert len(df) == 3  # very lazy test...


def test_read_barcodes(barcodes):
    df = read_barcodes(barcodes)
    assert len(df) == 12  # very lazy test...


def test_read_matrix(matrix):
    df = read_matrix(matrix)
    print("\n", df)
    assert len(df) == 8  # very lazy test...


# def test_matrix2widegdf(matrix, barcodes):
    # gdf = matrix2widegdf(matrix, barcodes)
    # # print("\n", gdf)
    # # print(gdf.index)
    # # print(gdf.dtypes)
    # assert len(gdf) == 7  # very lazy test...


def test_matrix2gdf(matrix, barcodes, features):
    '''convert matrix to long geodataframe with xy info from barcode table'''
    gdf = matrix2gdf(matrix, barcodes, features)    
    # print("\n")
    # print(gdf)
    # print(gdf.dtypes)
    assert len(gdf) == 8


# def test_get_extent(barcodes):
    # df = read_barcodes(barcodes)
    # xmin, ymin, xmax, ymax = get_extent(df)
    # assert (xmin, ymin, xmax, ymax) == (1,1,4,3)


# def test_read_layout():
#     df = read_layout('hiseq')
#     print(df)
#     print(df.loc[(2, 2112)].row)


# def test_index_genes():
#     df_all = pd.read_csv("~/data/seqscope/hd30-hml22-incol/merged.csv")
#     df = df_all['gene_name'].value_counts().reset_index()   # type: ignore
#     df.columns = ['gene_name', 'count']
#     df['cum_percent'] = (df['count'].cumsum() / df['count'].sum())
#  
#     df.to_csv("~/data/seqscope/hd30-hml22-incol/count.csv")
#     print(df.head())


# def test_extract_genes():
#     data_dir = "~/data/seqscope/hd30-hml22-incol/"  
#     src_fgb = data_dir + "merged.fgb"
#     dst_csv = data_dir + "merged_.csv"
#     command = _extract_genes(src_fgb, dst_csv) 

# def test_read_hexagon():
#     data_dir = "/Users/yonghah/data/seqscope/hd30-hml22-incol/lda"
#     fit_result = "LDA_hexagon.nFactor_10.d_18.lane_2.2112_2113_2212_2213.fit_result.tsv" 
#     df = pd.DataFrame(pd.read_csv(Path(data_dir) / fit_result, sep="\t"))
#     false_easting = -2666223
#     false_northing = 0
#     scale = 80
#     radius = 80 * 2 / math.sqrt(3)
#     # x, y is swapped
#     df['x'] = df['Hex_center_y'] * scale - false_easting 
#     df['y'] = df['Hex_center_x'] * scale - false_northing 
#     print(df)
#     # df['geometry'] = df.apply(
#     #     lambda row: create_hexagon(radius, row.x, row.y), axis=1)
#     # gdf = gpd.GeoDataFrame(df, geometry=df['geometry']).set_crs('EPSG:3857')
#     # gdf.to_file(Path(data_dir) / "test_hex.gpkg")
#     # print(gdf)

def test_factorde():
    df = pd.DataFrame(
        {
            'factor': [0, 0, 1, 1, 1],
            'gene': ['a', 'b', 'a', 'c', 'd'],
            'Chi2': [5, 2, 3, 4, 5],
            'pval': [.1, .2, .1, .01, .02],
        }
    )
    res = _conversion(df, topn=2)
    ans = json.dumps({
        '0':[
            {'factor':0,'gene':'a','Chi2':5,'pval':0.1},
            {'factor':0,'gene':'b','Chi2':2,'pval':0.2}],
        '1':[
            {'factor':1,'gene':'d','Chi2':5,'pval':0.02},
            {'factor':1,'gene':'c','Chi2':4,'pval':0.01}]
    }, indent=2, separators=(',', ':'))
    print(res)
    assert res == ans

