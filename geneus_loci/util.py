import pandas as pd


def read_features(features) -> pd.DataFrame:
    header = ['name', 'gene_name', 'desc', 'gene_id', 'total_count', 'counts']
    dtype_dict = {
        'name': str,
        'gene_name': str,
        'desc': str,
        'gene_id': 'int32',
        'total_count': 'int32',
        'counts': str
    }
    df = pd.read_csv(
            features, sep="\t", 
            names=header, 
            dtype=dtype_dict).set_index("gene_id")  # type: ignore
    df = df[['gene_name']]  # type: ignore
    return df


def read_barcodes(barcodes) -> pd.DataFrame:
    header = [
        'barcode', 'barcode_id', 'col1', 'col2', 'lane', 'tile',
        'y', 'x', 'counts']
    dtype_dict = {
        'barcode': str,
        'barcode_id': 'int32',
        'y': 'int32',
        'x': 'int32',
    }

    df = pd.read_csv(barcodes, sep="\t", names=header, 
            dtype=dtype_dict).set_index('barcode_id')  # type: ignore
    return df  # type: ignore


def read_matrix(matrix) -> pd.DataFrame:
    header = ['gene_id', 'barcode_id', 'cnt_spliced', 'cnt_unspliced', 'cnt_ambiguous']
    dtype_dict = {
        'gene_id': 'int32',
        'barcode_id': 'int32',
        'cnt_spliced': 'int16',
        'cnt_unspliced': 'int16',
        'cnt_ambiguous': 'int16',
    }
    df = pd.read_csv(   
        matrix, 
        sep=" ", names=header, 
        skiprows=3, dtype=dtype_dict)   # type: pandas:DataFrame
    df['cnt_total'] =  (
        df['cnt_spliced'] + \
        df['cnt_unspliced'] + \
        df['cnt_ambiguous']).astype('int16')   
    
    return df  

