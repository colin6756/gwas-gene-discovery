# GWAS-gene-discovery
Tool for discovering potential genes of interest from output of GWAS analysis software.




## Overview
The instructions below provide users with a copy of this program which can be directly used or adapted for their own project. 
The first component of the program searches through the databases of Ensembl Rest Server and returns Ensembl IDs of genes positioned within a designated base-pair distance around SNPs occurences in GWAS that are statistically associated to a phenotype.

The second component then input the gene IDs into Knetminer in addition to key word descriptions of the phenotypes contained within a plain text file. This will return for each gene a hyperlink to the network visualisations displaying QTLs, orthologs, publications etc related to the gene therefore accelerating and generating new insights for research.




## Prerequisites
* The script can run on any machine able to access linux terminal with either python 2 or python 3. 

* The program does not require heavy computational resources. However, as the user may prefer high performance computing the instructions on how to set up and run the program on Rothhpc4 server at Rothamsted Research managed by the Easybuild framework bas been included below. The User should read instructions specific to any other HPC frameworks.

* In addition to either Python version, the user should ensure they have installed Requests module into Python path. See **3. Installing requests** in **Instructions** on how to do this.

* Python virtual environments, e.g. virtualenv for python2 or pyvenv for python3. **Only for users with standard linux terminal without root permission.**




## Tutorial and usage instructions
This is a quick tutorial to get the user started by reproducing the outputs of map_snp_to_gene_vEN.py for 2 different GWAS output spreadsheets, GAPIT.MLM.DTF.GWAS.Results.csv and GAPIT.MLM.blupWidth.GWAS.Results.csv as seen in the 2 directories of the same names. The tutorial generally assume the user has access to Rothamsted Research facility's Rothhpc4 cluster.

#### 1.Downloading the repository
Clone this repository with the GitHub URL using either Git or a Git GUI. The user should obtain a directroy named gwas-gene-discovery containing identical contents to the GitHub repository.

#### 2. Accessing compute node of Rothhpc4 Server managed by Easybuild
 Requests is already installed onto standard compute nodes of Rothhpc4 server which can be logged in as shown below. For machines without access to Rothamsted's HPC clusters, read **standard linux terminals** in step 3.

The user can check available compute nodes by the command:
```
sinfo 
```
If available, login to a standard compute node on Rothhpc4 using:
```
srun --pty bash -i
```

#### 3.OPTIONAL: Setting up a virtual environment on Rothhpc4 HPC cluster or standard Linux Terminal

###### Virtual environment on Rothhpc4 with Easybuild
A virtual environment is not compulsory for Rothhpc4 users as Requests is pre-installed in Python path on compute nodes. However, for other machines with EasyBuild frameworks outside of Rothamsted Research, the user should set up a virtual environment and install requests by following instructions below.

Check all the available versions of python currently on cluster:
```
module avail Python
```
Afer a Python2 or Python3 version has been selected either edit the sbatch script in this repository, virtualenv_setup.sbatch or execute the commands below.

```
module load <Python version>
virtualenv <name of Python virtual environment>
source </path to env>/bin/activate/
```
The user can return to the virtual environment in another session with:
```
module load <Python version>
source </path to env>/bin/activate/
```
###### Virtual environment in standard linux terminal
If the User is on a standard linux terminal, virtualenv for python2 and/or pyvenv must be installed previously.
Set up virtual environment by:
```
virtualenv <Python virtual environment name>
export PYTHONPATH="/home/apps/python/lib64/<python version>/site-manager"
source <path to virtual environment>/bin/activate
```
The user may access the virtual environment in another session by:
```
source <path to virtual environment>/bin/activate
```
  
#### 4.Installing requests
Requests is needed for the steps that send HTTP request protocols found in the script. The following commands can install requests either within or outside a virtual environment:
```
pip install requests
```

#### 5.Execution of script
The command:
```
python map_snp_to_gene_vEn.py -h
```
Returns the usage of the script as the following:
```
map_snp_to_gene_vEn.py [-h] [-p P] [-d D] file list
```
The **mandatory arguments** are:
* File. A spreadsheet containing the results of GWAS analysis. The fields of spreadsheet should be arranged in the order below as the script was originally designed for GAPIT software outputs (examples being 2 csv files in repository).:

  SNP | Chromosome | Position | P.value | maf | nobs | Rsquare.of.Model.without.SNP | Rsquare.of.Model.with.SNP | FDR_Adjusted_P-values


* A plain text file containing one or more short description of the phenotype or phenotypes genes of interest are suspected to influence. The keywords should be vertically listed line by line. An example list, mock_keyword_list.txt can be found in the repository.

The **optional arguments** are:
* logPthreshold: -log10(p-value of SNPs). It is used to extract SNPs strongly associated to phenotypes of interest as indicated by the association test of GWAS. The default value is 6 as per standard of majority of GWAS research papers.
* Distance: The distance in base-pairs upstream and downstream from a SNP exceeding loPthreshold. All genes positioned within this genomic length are returned. 1kbp is the default value and this means a SNP occurence is upstream, downstream or within gene or genes located in this 1kbp region.

If the User has either a standard or Easybuild terminal set up with requests installed, they can run the following commands. This will reproduce the directories: /MLM.blupWidth.GWAS.Results and /MLM.DTF.GWAS.Results which are example outputs produced with all optional parameters set to default for the 2 case study spreadsheets in repository.

```
python map_snp_to_gene_vEn.py GAPIT.MLM.DTF.GWAS.Results.csv mock_keyword_list.txt
```
```
python map_snp_to_gene_vEn.py GAPIT.MLM.DTF.GWAS.Results.csv mock_keyword_list.txt
```

#### 6. Output information
Inspect directories /MLM.blupWidth.GWAS.Results and /MLM.DTF.GWAS.Results. The script has produced a directory of the same name for each input spreadhseet. Within each directory, 3 files can be found:
* filtered_snps.txt. This lists all the significant SNPs incrementally named from 1. Use the row number in spreadsheet to track the exact SNP ID. e.g. In /MLM.blupWidth.GWAS.Results, SNPnum 36524 in filtered_snps.txt is the 36524th SNP found in the input CSV spreadsheet, its ID is 23974957.
* summary_genes_discovered.txt. This contains the significant SNPs and the geneIDs found within the user-defined or default distance around the SNP. Additional information such as snp effects are included.
* knet_summary.txt. This file contains for each geneID from summary_genes_discovered, the URL link to Knetminer's network view showing orthologous relationships, traits, publications etc with a KnetScore ranking predicted relevance to traits in keyword list.




## External tools included
Ensembl rest server.
Knetminer




## Versions
This is the most stable and latest script. An older archived version of this script exists but takes input of genomic references of Oryza Sativa from IRRI instead of Ensembl.




## Authors
TBC


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
TBC
