# GWAS-gene-discovery
Tool for discovering potential genes of interest from output of GWAS analysis software.

## Introduction
The instructions below provide users with a copy of this program which can be directly used or adapted for their own project. 
The first component of the program searches through the databases of Ensembl Rest Server and returns Ensembl IDs of genes positioned within a designated base-pair distance around SNPs occurences statistically associated to a phenotype subjected to GWAS.

The second component then input the gene IDs into Knetminer in addition to key words which describes the phenotypes contained within a plain text file. This will return for each gene a hyperlink to the network visualisations displaying QTLs, orthologs, publications etc related to the gene therefore accelerating and generating new insights for research.

## Prerequisites
* The script can run on any machine with either python 2 or python 3. 

* The program does not need heavy computational resources. However, The User may nevertheless want to execute the program on a High Performance Computing cluster. Therefore, the instructions on how to set up and run the program on Rothhpc4 server in Rothamsted Research which has the Easybuild framework bas been included below.

* In addition to either Python version, the user should ensure they have installed requests module into Python path. See 3. Installing requests in Instructions on how to do this.

## Instructions
#### 1.Downloading the repository
Clone this repository by clicking on "Clone or download" button, copy the URL and either input it into a Github GUI program or if git is installed in bash terminal execute the following. The user should find a copied directory named gwas-gene-discoveryV2 with all the contents of the Github repository:
```
git clone https://github.com/Citrolius/gwas-gene-discoveryV2.git
```

#### 2.Setting up a virtual environment on Rothhpc4 HPC cluster
This section assumes the user has access to Rothamsted Research facility's Rothhpc4 cluster or a computer running Linux with Easybuild framework.
A login node is accessed by the User after logging into the server. The user should execute the following to check available compute nodes:
```
sinfo 
```
If available a standard compute node can then be logged in on Rothhpc4 using:
```
srun --pty bash -i
```
On the compute node, the user should then check all the available versions of python currently on cluster:
```
module avail Python
```
To set up a virtual environment, the User can either run the sbatch script included in repository, virtualenv_setup.sbatch or execute the commands below.

```
module load <Python version>
virtualenv <name of Python virtual environment>
```

The virtual environment can later be activated with:
```
module load <Python version>
source </path to env/bin/activate/>
```
#### 3.Installing requests
Requests is needed for the steps that send HTTP request protocols in the script. The following commands can install request either within or outside a virtual environment:

```
pip install requests
```

#### 4.Input data and execution
The usage of the script is as following
```
map_snp_to_gene_vEn.py [-h] [-p P] [-d D] file list
```
The **mandatory / positional arguments** are:
* A spreadsheet containing the results of GWAS analysis, the fields of spreadsheet should be arranged in the order below:


SNP | Chromosome | Position | P.value | maf | nobs | Rsquare.of.Model.without.SNP | Rsquare.of.Model.with.SNP | FDR_Adjusted_P-values


* A plain text file of a list of keywords describing the phenotype the genes are believed to be associated to.

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
