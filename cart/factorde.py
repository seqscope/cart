# codes for processing differential expressions in factor analysis
# converts de data to json grouped by factor 

import argparse
import json
from pathlib import Path
import pandas as pd


def main():
    """
    run script for converting factor de to json 
    ```
    $ python -m cart.factorde -i de.tsv.gz -o output.json 
    ````
    """
    parser = argparse.ArgumentParser(
        description="Converting factorization result to hexgagon file")
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help="Input tsv or tsv.gz file path")
    parser.add_argument(
        "-o", "--output", type=str, default="output.json",
        help="Output file name")
    parser.add_argument(
        "-n", "--topn", type=int, default=20,
        help="top n genes. All genes included if n=0")
    args = parser.parse_args()
    conversion(args.input, args.output, args.topn)


def conversion(input, output, topn):
    # columns: gene, factor, Chi2, pval, FoldChange, gene_tot
    df = read_table(input)
    res_dict = _conversion(df, topn=topn)
    with open(output, 'w') as f:
        f.write(res_dict)


def _conversion(df, topn=2):
    res = (df
        .sort_values(['factor','Chi2'], ascending=False)
        .groupby('factor')
        .apply(lambda x: 
                   x.head(topn).to_dict(orient='records') if topn 
                   else x.to_dict(orient='records'))
    ).to_json(indent=2)
    return res


def read_table(tsv_path):
    """ read de tsv and convert it to dataframe
    """
    df = pd.DataFrame(pd.read_csv(tsv_path, sep="\t"))  
    return df 


if __name__=='__main__':
    main()

