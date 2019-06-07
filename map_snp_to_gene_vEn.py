#!/usr/bin/python
from __future__ import print_function
import os, math, datetime, requests, json, argparse, shutil, sys

def mkfolder():
    '''Create a folder for each gapit results, copy result.csv and reference into that directory.
    All results will then be generated within it. The main function will take the script back into parent.''' 
    print("Commenced at {}".format(datetime.datetime.now()))
    folder=str(args.f)[6:-4]
    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.mkdir(folder)
        shutil.copy(args.f, folder)
        shutil.copy(args.l, folder)
        os.chdir(folder)
    else:
        os.mkdir(folder)
        shutil.copy(args.f, folder)
        shutil.copy(args.l, folder)
        os.chdir(folder)
    # end of mkfolder()

def sigsnps(filtered_snps):
    '''Extract relevant metrics e.g. chromosome, base position and p-value of SNPs into a txt.
    Condense information while adding the new metric of logP and naming SNPs based on incrementing
    integers instead of id.'''
    with open(args.f, "r") as f:
        next(f)
        logP_threshold = args.p
        with open(filtered_snps, "w") as ft:
            snp = 0
            print("{}\t{}\t{}\t{}\t{}".format("SNPnum","CHR","snpBP","P","logP"), file=ft)
            for line in f:
                snp += 1
                col = line.split(",")
                chro_snp = col[1]
                bp_snp = col[2]
                pval = float(col[3])
                logP = -math.log10(pval)

                if logP > logP_threshold:
                    server = "http://rest.ensembl.org"
                    ext = "/overlap/region/oryza_sativa/{}:{}-{}:1?feature=variation".format(chro_snp,bp_snp,bp_snp)
                    r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
                    decoded = r.json()

                    if not r.ok:
                        r.raise_for_status()
                        sys.exit()
                        print("Request has failed to get API")

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
            print("GENE\tCHR\tSNPnum\tsnpBP\tP\tlogP\tSNPeff\tallele\tdesignation\tstrand", file=fs)
            for line in fr:
                col = line.split("\t")
                chrom = col[1]
                position = int(col[2])
                start = position - args.d
                end = position + args.d
                snpnum = col[0]
                pval = col[3]
                logP = col[4]
                snpeffect = col[5]
                alleleinfo = str(col[6]).replace("\n", "")
                
                #ASK KEYWAN WHY WE WANT TO PUT THE SNP'S POSITION INTO OUR FILE INSTEAD OF GENE BP?
                #server = "http://rest.ensemblgenomes.org"
                server = "http://rest.ensembl.org"
                ext = "/overlap/region/oryza_sativa/{}:{}-{}:1?feature=gene".format(chrom, start, end)

                r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
                
                
                #print(r.json())
                if len(r.json()) != 0:
                    decoded=r.json()[0]
                    gene = decoded[u'gene_id']
                    description = decoded[u'description']
                    sense = decoded[u'description']

                    print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(gene, chrom, snpnum, position, pval, logP, snpeffect, alleleinfo, description, sense), file=fs)
                                   
    #end of get genes

def knetapi(disc_genes, genetab):
    '''Use the genes from the summary file to search for Knetminer genome api.'''
    with open(disc_genes, "r") as fs:
        next(fs)
        with open(genetab, "w") as fj:
            genes = []
            with open(args.l, "r") as fl:
                pheno = []
                for line in fs:
                    col = line.split("\t")
                    genes.append(col[0])
                genelist = (",").join(genes) #join all iterative elements by ,
                #print(genelist)
                for line in fl:
                    pheno.append(line.rstrip())
                    print(pheno)
                #use str.join() to convert multiple elments in a list into one string.
                keyw = "%20OR%20".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
                link = "http://knetminer.rothamsted.ac.uk/riceknet/genome?"
                parameters = {"keyword":keyw, "list":genelist}
                r = requests.get(link, params=parameters)
                
                #check if request is succesfsul.
                if not r.ok:
                    r.raise_for_status()
                    sys.exit()
                
                #printing out genetable to a file.
                decoded = str(r.json()[u'geneTable'])
                print(decoded, file=fj)        
    #end of knetapi

def knetsummary(genetab, knet):
    '''Extract the scores only.'''
    with open(genetab, "r") as f:
        next(f)
        with open(knet, "w") as fs:
            with open(args.l, "r") as fl:
                pheno = []
                for line in fl:
                    pheno.append(line.rstrip())
                    print(pheno)
                for line in f:
                    if line == "\n":
                        continue
                    col = line.split("\t")
                    score=str(col[6]) 
                    genes=col[1]
                    keyw = "+OR+".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
                    print(type(keyw))
                    #parameters = {"keyword":keyw, "list":genes}
                    link="http://knetminer.rothamsted.ac.uk/riceknet/genepage?list={}&keyword={}".format(genes, keyw)
                    #r=requests.get(link, params=parameters)
                    r=requests.get(link)
                    print(r.url)
                    print("{}\t{}\t{}".format(genes, score, r.url), file=fs)
#End of block 7 to print genes, scores and url into scores.txt


def main():
    
    try:
        print("Creating directory for results.")
        mkfolder()
    except:
        raise

    try:
        filtered_snps="filtered_snps.txt"
        print("reading from: {}".format(args.f))
        print("extracting SNPs exceeding logP threshold of {} into: {}".format(args.p, filtered_snps))
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
        genetab="genetable.txt"
        print("Searching with Knetminer for related genes to genes discovered from Ensembl.")
        knetapi(disc_genes, genetab)
    except:
        raise

    try:
        genetab="genetable.txt"
        knet="knet_summary.txt"
        print("Producing summary file containing related genes found with Knetminer, their respective Knetscore and hyperlinks to network view.")
        knetsummary(genetab, knet)
    except:
        raise


if __name__ == "__main__":
    #creating parameters for the end-user.
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="name of .csv output from GAPIT gwas tool")
    parser.add_argument("-p", help="integer value of logP threshold (-log10 of pvalue) for SNPs", type=int)
    parser.add_argument("-d", help="integer value of a distance window in base pair upstream or downstream of a SNP exceeding logPthreshold.", type=int)
    parser.add_argument("-l", help="a plain text file containing description of phenotypes of interest line by line")
    args = parser.parse_args()

    main()

    print("The entire pipeline finished at:")
    print(datetime.datetime.now())

    exit



    