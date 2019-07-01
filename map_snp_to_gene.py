#!/usr/bin/python
from __future__ import print_function
import os, math, datetime, requests, json, argparse, shutil, sys
import pandas as pd
import numpy as np

def mkfolder():
    '''Create a folder for each gapit results, copy result.csv and reference into that directory.
    All results will then be generated within it. The main function will take the script back into parent.'''
    print("Commenced at {}".format(datetime.datetime.now()))
    folder=str(args.file)[6:-4]
    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.mkdir(folder)
        shutil.copy(args.file, folder)
        shutil.copy(args.list, folder)
        os.chdir(folder)
    else:
        os.mkdir(folder)
        shutil.copy(args.file, folder)
        shutil.copy(args.list, folder)
        os.chdir(folder)
    # end of mkfolder()

def sigsnps(filtered_snps):
    '''Extract relevant metrics e.g. chromosome, base position and p-value of SNPs into a txt.
    Condense information while adding the new metric of logP and naming SNPs based on incrementing
    integers instead of id.'''
    with open(args.file, "r") as f:
        next(f)
        logP_threshold = args.logP
        with open(filtered_snps, "w") as ft:
            #name snp incrementally as 1, 2, 3 etc in chronology.
            snp = 0
            #add headers
            print("{}\t{}\t{}\t{}\t{}".format("SNPnum","CHR","snpBP","P","logP"), file=ft)
            for line in f:
                snp += 1
                col = line.split(",")
                chro_snp = col[1]
                bp_snp = col[2]
                pval = float(col[3])
                logP = -math.log10(pval)
                if args.species == 1:
                    species="oryza_sativa"
                elif args.species == 2:
                    species="triticum_aestivum"
                elif args.species == 3:
                    species="arabidopsis_thaliana"
                #only do requests for SNPs exceeding threshold.
                if logP > logP_threshold:
                    server = "http://rest.ensembl.org"
                    ext = "/overlap/region/{}/{}:{}-{}:1?feature=variation".format(species, chro_snp,bp_snp,bp_snp)
                    r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
                    decoded = r.json()
                    #check if requests is successful
                    if not r.ok:
                        r.raise_for_status()
                        sys.exit()

                    for i in decoded:
                        if i == "\n":
                            continue
                        data=decoded[0]
                        snpeffect = str(data[u'consequence_type'])
                        alleleinfo = str(data[u'alleles'])
                    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(snp,chro_snp,bp_snp,pval,logP, snpeffect, alleleinfo), file=ft)
    # end of formatcsv

def summary(filtered_snps, disc_genes):
    '''Query on ensembl for genes ocurring within a specified distance in bp of each significant SNPs.
    Produce a summary file of the genes as well as the phenotypes and functions linked to the genes provided by ensembl.'''
    with open(filtered_snps, "r") as fr:
        next(fr)
        with open(disc_genes, "w") as fs:
            #add headers
            print("GENE\tSNP_CHROMOSOME\tSNP_number\tSNP_Base_Position\tp-value\tlogP\tSNP_effect\tallele_info\tGene_description", file=fs)
            for line in fr:
                col = line.split("\t")
                chrom = col[1]
                position = int(col[2])
                start = position - args.distance
                end = position + args.distance
                snpnum = col[0]
                pval = col[3]
                logP = col[4]
                snpeffect = col[5]
                alleleinfo = str(col[6]).replace("\n", "")
                if args.species == 1:
                    species="oryza_sativa"
                elif args.species == 2:
                    species="triticum_aestivum"
                elif args.species == 3:
                    species="arabidopsis_thaliana"

                server = "http://rest.ensembl.org"
                ext = "/overlap/region/{}/{}:{}-{}:1?feature=gene".format(species, chrom, start, end)

                r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})

                if not r.ok:
                    r.raise_for_status()
                    sys.exit()

                #print(r.json())
                if len(r.json()) != 0:
                    decoded=r.json()[0]
                    gene = decoded[u'gene_id']
                    description = decoded[u'description']
                    sense = decoded[u'description']

                    #add values to headers
                    print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(gene, chrom, snpnum, position, pval, logP, snpeffect, alleleinfo, description), file=fs)
    #end of get genes

def append_summary(disc_genes):
    '''Query Knetminer and append to summary: Knetscore assessing gene relevance and
    genepage url for network view displaying orthology, traits etc relating to each gene discovered'''
    with open(args.list, "r") as fk:
        pheno=[]
        for line in fk:
            pheno.append(line.rstrip())

        #defining variables for genepage url later on.
        summary=pd.read_csv(disc_genes, sep="\t")
        network_view=[]
        keyw1 = "%20OR%20".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
        genestr=(",").join(list(summary[u'GENE']))
        print("The genes found on ensembl:")
        print(set(summary[u'GENE']))
        print("The phenotypes they are suspected to influence:")
        print(pheno)
        keyw2 = "+OR+".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
        #define species
        if args.species == 1:
            species="riceknet"
        elif args.species == 2:
            species="wheatknet"
        elif args.species == 3:
            species="araknet"

        #obtaining knetscores for genes
        link="http://knetminer.rothamsted.ac.uk/{}/genome?".format(species)
        parameters={"keyword":keyw1, "list":genestr}
        r=requests.get(link, params=parameters)

        if not r.ok:
                r.raise_for_status()
                sys.exit()

        #extract unicode string of geneTable decoded from json
        decoded=r.json()[u'geneTable'].split("\t")
        #remove space or newline at the end
        decoded=(decoded)[:-1]

        colnum=9
        #tabulate genetable into 9 columns.
        genetable=np.array(decoded).reshape(len(decoded)//colnum, colnum)
        genetable=pd.DataFrame(genetable[1:,:], columns=genetable[0,:])

        knetgenes=list(genetable[u'ACCESSION'])
        knetscores=list(genetable[u'SCORE'])

        #map genes to snps via a dictionary.
        knetdict=dict(zip(knetgenes, knetscores))
        ordered_score=[]
        for i in summary[u'GENE']:
            #convert gene id to upper case to avoid sensitivity issues.
            i=i.upper()
            try:
                ordered_score.append(knetdict[u'{}'.format(i)])
                # obtaining knetminer urls
                genepage="http://knetminer.rothamsted.ac.uk/{}/genepage?list={}&keyword={}".format(species, i, keyw2)
                r=requests.get(genepage)
                print(r.url)
                network_view.append(r.url)
            except KeyError:
                print("{} not found in Knetminer".format(i))
                ordered_score.append("N/A")
                network_view.append("N/A. Gene not in Knetminer.")
                continue
        #adding new columns to summary.
        summary[u'SCORE'] = ordered_score
        summary[u'network_view']=network_view
        print("These are the URL to Knetminer networks. Also available in output summary.")
        print(network_view)

        summary.to_csv(disc_genes, sep="\t", index=False)
    #end of append_summary function.


def main():

    try:
        print("Creating directory for results.")
        mkfolder()
    except:
        raise

    try:
        filtered_snps="filtered_snps.txt"
        print("reading from: {}".format(args.file))
        print("extracting SNPs exceeding logP threshold of {} into: {}".format(args.logP, filtered_snps))
        sigsnps(filtered_snps)
    except:
        raise

    try:
        filtered_snps="filtered_snps.txt"
        disc_genes="summary_genes_discovered.txt"
        print("Searching for ensembl ebi for genes associated to SNPS. Producing summary file.")
        summary(filtered_snps, disc_genes)
    except:
        raise

    try:
        disc_genes="summary_genes_discovered.txt"
        print("Searching Knetminer to append score and networks of genes discovered from Ensembl.")
        append_summary(disc_genes)
    except:
        raise


    os.remove(args.list)
    os.remove(args.file)


if __name__ == "__main__":
    #creating parameters for the end-user.
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="name of .csv output from GAPIT gwas tool. For specific formatting, check on ReadMe", type=str)
    parser.add_argument("list", help="a plain text file containing description of phenotypes of interest line by line")
    parser.add_argument("species", help="Choose an integer out of three to select the species of organism subjected to gwas. 1 being rice, 2 being wheat and 3 being arabidopsis", type=int)
    parser.add_argument("--logP", default=6, help="integer value of logP threshold (-log10 of pvalue) for SNPs", type=int)
    parser.add_argument("--distance", default=1000, help="integer value of a distance window in base pair upstream or downstream of a SNP exceeding logPthreshold.", type=int)
    args = parser.parse_args()

    main()

    print("The entire pipeline finished at:")
    print(datetime.datetime.now())

    exit
