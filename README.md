# gwas-gene-discoveryV2
This version of the pipeline would take the gapit tabular result ending in .csv and filter out the SNPs of significant p-value before searching on Ensembl for genes within 1000bp for each.

# dependencies
The script can run on either python2 or python3 environments. The user must install requests into python path beforehand.

# usage
Python map_snp_to_gene_vEn.py -f <the gapit tabular output in csv> -p <a user defined logP threshold value>

By running the pipeline on the 2 csv files, the user will find 2 separate directories produced identical to the directories in /example directory. They are named after the input Gapit tabular inputs.

Should the user stop running the script before its completition a later run will overwrite the previous directory.
