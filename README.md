# GWAS-gene-discovery

This version of the pipeline would take the gapit tabular result ending in .csv and filter out the SNPs of significant p-value before searching on Ensembl for genes within 1000bp for each.

## Getting Started

The instructions below provides users with a copy of this tool which can be directly used or adapted for their own project. 
The first component of the program searches the database of Ensembl Rest Server and returns potential genes of interest located within a designated base-pair distance of SNPs occurences linked to one or more phenotypic traits indicated by a Genome Wide Association Study.

The second component then input the genes into Knetminer along with any phenotypes if they are suggested by the user. This will return for each gene a hyperlink to the network visualisations of QTLs, orthologs, traits or role in biochemical pathways and publications regarding the gene, to accelerate and generate new insights for research.

## Prerequisites
* The script was designed for any machine able to run either python 2 or python 3. 

* In addition to either Python version, the user should ensure they have installed requests module into python path. For users who are administrators, this can be done by:

for python 2
```
pip install requests
```
or for python 3
```
pip3 install requests
```
For non-administrator users, setting up a virtual environment is recommended to acquire requests. See instructions below which details on how to do this on Rothhpc4 HPC clusters.

* There is no demand for heavy computational resource but the user may want to execute the program on a High Performance Computing cluster regardless. Therefore, the instructions below includes how set up and run the program on Rothhpc4 server in Rothamsted Research which has the Easybuild framework. citations needed?

## Instructions
Python map_snp_to_gene_vEn.py -f <the gapit tabular output in csv> -p <a user defined logP threshold value>

By running the pipeline on the 2 csv files, the user will find 2 separate directories produced identical to the directories in /example directory. They are named after the input Gapit tabular inputs.

Should the user stop running the script before its completition a later run will overwrite the previous directory.

## Built With

## Versioning

## Authors

## License

## Acknowledgement
