import subprocess
import argparse
import os
from pathlib import Path
from multiprocessing import Pool

import pandas as pd
import numpy as np


def main():
    """
    Example:
    $ python -m cart.split \
    -s ~/data/seqscope/hd30-hml22-incol/merged.fgb \
    -o ~/data/seqscope/hd30-hml22-incol/output \
    -t 0.05

    Input:
    merged.fgb: all gene expressions in one layer 'all'
    
    Output:
    *.fgb: point layer named 'all' for single gene
    merged.csv: gene column extracted from merged.fgb. used for counting
    count.csv: gene_name, count, cum_fraction, freq
    freq.json: {'freq'{'Lypd8': 0.0153, 'Cyp2c70':0.0144, ...}}
    """
    parser = argparse.ArgumentParser(description="Convert SeqScope data to geographic format")
    parser.add_argument(
        "-s", "--source", type=str, required=True, 
        help="source file")
    parser.add_argument(
        "-o", "--out", type=str, required=True,
        help="Output dir")
    parser.add_argument(
        "-c", "--cpu", type=int, default=6,
        help="number of processes") 
    parser.add_argument(
        "-t", "--threshold", type=float, default=.8,
        help="inclusion threshold. top X genes are included") 
    args = parser.parse_args()
    run(args.source, args.out, args.threshold, args.cpu)
 

def run(src_fgb, output_path, threshold=0.05, cpu=4):
    output_dir = Path(output_path).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    dst_csv = output_dir / "merged.csv"
    
    _extract_genes(src_fgb, dst_csv)
    df = _count_genes(dst_csv)
    df.to_csv(output_dir / "count.csv", index=False)
   
    for thres in np.arange(0.05, 1.05, .05):
        print(f"{thres:.2f}", len(df[df.cum_fraction < thres]))
    df_split = df[df['cum_fraction'] < threshold][['gene_name', 'freq']]
    df_split.set_index(['gene_name']).to_json(output_dir / "split.json")
    genes_to_split = df_split['gene_name'].tolist()
    # _split_fgb(src_fgb, output_dir, genes_to_split, cpu)


def _extract_genes(src_fgb, dst_csv):
    """
    create command for reading gene_name columns 
    from full gene fgb.
    ogr2ogr -f CSV -sql "select gene_name from \"all\"" \
    merged.csv merged.fgb
    """
    command = "ogr2ogr -f CSV " +\
        "-sql \"select gene_name from \\\"all\\\"\" "+\
        f"{dst_csv} {src_fgb}"
    print(command)
    subprocess.call([command], shell=True)
    # return command


def _count_genes(gene_csv, cutoff=1.0):
    df_all = pd.read_csv(gene_csv)
    df = df_all['gene_name'].value_counts().reset_index()   # type: ignore
    df.columns = ['gene_name', 'count']
    df['cum_fraction'] = (df['count'].cumsum() / df['count'].sum())
    df['freq'] = (df['count'] / df['count'].sum())

    df.to_csv("~/data/seqscope/hd30-hml22-incol/count.csv")
    df = df[df['cum_fraction'] <= cutoff]
    return df


def _split_fgb(src_fgb, output_dir, gene_names, cpu=4):
    """
    run the commands 
    """
    args_list = map(lambda t: (src_fgb, output_dir, t), gene_names)
    with Pool(cpu) as p:
        p.starmap(_split_fgb_single, args_list)


def _split_fgb_single(src_fgb, output_dir, gene_name):
    """
    run command for ogr2ogr 
    ogr2ogr -f FlatGeoBuf -where "gene_name='Pyy'" \
    Pyy.fgb merged.fgb 
    """
    command = "ogr2ogr -f FlatGeoBuf " +\
        f"-where \"gene_name='{gene_name}'\" "+\
        f"{output_dir}/{gene_name}.fgb {src_fgb}"
    subprocess.call(command, shell=True)


if __name__=="__main__":
    main()
