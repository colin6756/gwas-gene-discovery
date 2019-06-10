# GWAS-gene-discovery
Tool for discovering potential genes of interest from output of GWAS analysis software.

## Getting Started
The instructions below provide users with a copy of this program which can be directly used or adapted for their own project. 
The first component of the program searches through the databases of Ensembl Rest Server and returns Ensembl IDs of genes positioned within a designated base-pair distance around SNPs occurences statistically associated to a phenotype subjected to GWAS.

The second component then input the gene IDs into Knetminer in addition to key words which describes the phenotypes contained within a plain text file. This will return for each gene a hyperlink to the network visualisations displaying QTLs, orthologs, publications etc related to the gene therefore accelerating and generating new insights for research.

## Prerequisites
* The script was designed for any machine able to run either python 2 or python 3. 

* While the program does not require heavy computational resource the User may want to execute the program on a High Performance Computing cluster regardless. Therefore, the instructions below includes how set up and run the program on Rothhpc4 server in Rothamsted Research which has the Easybuild framework.

* In addition to either Python version, the user should ensure they have installed requests module into python path. See the instructions section, 3. Installing requests on how to do this.

## Instructions
#### 1.Downloading the repository
Clone this repository by clicking on "Clone or download" button, copy the URL and either input it into a Github GUI program or if git is installed in bash terminal execute the following:
```
git clone https://github.com/Citrolius/gwas-gene-discoveryV2.git
```
The user should find a copied directory named gwas-gene-discoveryV2 with all the contents of the Github repository.

#### 2.Setting up a virtual environment on Rothhpc4 HPC cluster
This section assumes the user has access to Rothamsted Research facility's Rothhpc4 cluster or any machine with Easybuild managing its linux servers.
A login node is accessed by the User after logging into the server. The user should execute the following to check available compute nodes:
```
sinfo 
```
If available a standard compute node can be logged in on Rothhpc4 using:
```
srun --pty bash -i
```
Once on a compute node, one can check all the available versions of python currently on cluster:
```
module avail Python
```
To set up a virtual environment, the one can either run the sbatch script, virtualenv_setup.sbatch in the repository or continue reading the commands below.

A python version has to be loaded prior to setting up its virtual environment:
```
module load <Python version>
```
The user can then set up a virtual environment using virtualenv:
```
virtualenv <name of Python virtual environment>
```
The virtual environment can later be activated with:
```
source </path to env/bin/activate/>
```
#### 3.Installing requests
Requests is a concise and easy library for sending HTTP request protocols from python. The following commands installs request either within or outside a virtual environment:

* for python 2 or within virtual environment of either Python version.
```
pip install requests
```

#### 4.Input data and execution
By running the help option,
```
Python map_snp_to_gene_vEN.py -h
```
the python script should return the following output:
```
usage: map_snp_to_gene_vEn.py [-h] [-f F] [-p P]

optional arguments:
  -h, --help  show this help message and exit
  -f F        name of .csv output from GAPIT gwas tool
positional arguments:  
  -p P        integer value of logP threshold (-log10 of pvalue) for SNPs. Default value is 6
  -l L        a plain text file containing a list of phenotypes the genes are suspected to be causative or has strong influence on
  -d D        distance of the base-pair window around SNP for which genes are returned
  -sp SP      species
 ```
The usage of the script is as following
```
Python map_snp_togene_vEN.py -f [spreadsheet of GWAS result] -p [logPthreshold] -d [Distance] -l [Keyword list] -sp [species]
```
The **mandatory argument** are:
* A spreadsheet containing the results of GWAS analysis, the fields of spreadsheet should be arranged in the order below:
SNP | Chromosome | Position | P.value | maf | nobs | Rsquare.of.Model.without.SNP | Rsquare.of.Model.with.SNP | FDR_Adjusted_P-values
* species: The species of organism population of the GWAS. The taxonomy however, must be consistent with Ensembl's rest server. Please check the file specieslist.txt in the repository for correct taxonomy of species to input.

The **optional arguments** are:
* logPthreshold: -log10 of pvalue. It is used to extract SNPs with a significant statistic association to phenotype divisions in GWAS.
* Distance: The distance window upstream and downstream from a SNP exceeding loPthreshold for which genes positioned within are returned.
* Keyword list: A list containing phenotypic traits the user wants to include to aid the Knetminer search for orthologs associated genes found by GWAS. There should be nothing delimiting between each keyword which are written line by line.
e.g.
Germination rate
Mesocotyl length

## Built With
HTTP request for humans.
Ensembl rest server.
Knetminer
## Versioning
This is the most stable and latest script. An older archived version of this script exists but takes input of genomic references of Oryza Sativa from IRRI instead of Ensembl.
## Authors
William -for the sbatch script.
## License
MIT license.
## Acknowledgement
Keywan-Hassani Pak
William
IRRI
GAPIT
Ensembl
Knetminer
Rothamsted Resarch
