import io

import pytest
import pandas as pd
import geopandas as gpd

from geneus_loci import (
    __version__,
)
from geneus_loci.convert import (
    matrix2gdf,
    read_barcodes,
    read_features,
    read_matrix,
)
from geneus_loci.util import (
    read_barcodes,
    read_features,
    read_matrix,
)
from geneus_loci.meta import (
    # get_extent,
    read_layout,
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


def test_read_layout():
    df = read_layout('hiseq')
    print(df)
    print(df.loc[(2, 2112)].row)


