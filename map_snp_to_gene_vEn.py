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
        os.chdir(folder)
    else:
        os.mkdir(folder)
        shutil.copy(args.f, folder)
        os.chdir(folder)
    # end of mkfolder()

def formatcsv(formated):
    '''Extract relevant metrics e.g. chromosome, base position and p-value of SNPs into a txt.
    Condense information while adding the new metric of logP and naming SNPs based on incrementing
    integers instead of id.'''
    with open(args.f, "r") as f:
        next(f)
        with open(formated, "w") as ft:
            snp = 0
            print("{}\t{}\t{}\t{}\t{}".format("SNPnum","CHR","snpBP","P","logP"), file=ft)
            for line in f:
                snp += 1
                col = line.split(",")
                chro = col[1]
                bp = col[2]
                pval = float(col[3])
                logP = -math.log10(pval)
                print("{}\t{}\t{}\t{}\t{}".format(snp,chro,bp,pval,logP), file=ft)
        ft.close()
    f.close()
    # end of formatcsv

def sigsnps(formated, filtered_snps):
    '''Filter and extract SNPs and their metrics only if they are above logP threshold specified by user.
    Also acquires the SNP effects and allele information / base change from ensembl.'''
    with open(formated, "r") as ft:
        next(ft)
        logP_threshold = args.p
        with open(filtered_snps, "w") as fr:
            print("SNPnum\tCHR\tsnpBP\tP\tlogP\tSNPeff\talleleinfo", file=fr)
            for line in ft:
                col = line.split("\t")
                snp = col[0]
                chr_snp = int(col[1])
                bp_snp = int(col[2])
                pval = float(col[3])
                logP = float(col[4])

                if logP > logP_threshold:
                    #server = "http://rest.ensemblgenomes.org"
                    #old server is down.
                    server = "http://rest.ensembl.org"
                    ext = "/overlap/region/oryza_sativa/{}:{}-{}:1?feature=variation".format(chr_snp,bp_snp,bp_snp)
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
                    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(snp,chr_snp,bp_snp,pval,logP, snpeffect, alleleinfo), file=fr)
        fr.close()
    ft.close()
    #end of sigsnps

def summary(filtered_snps, disc_genes):
    '''Query on ensembl for genes ocurring within or 1000bp downstream of upstream of each significant SNPs.
    Produce a summary file of the genes as well as the phenotypes and functions linked to the genes provided by ensembl.'''
    with open(filtered_snps, "r") as fr:
        next(fr)
        with open(disc_genes, "w") as fs:
            print("GENE\tCHR\tSNPnum\tsnpBP\tP\tlogP\tSNPeff\tallele\tdesignation\tstrand", file=fs)
            for line in fr:
                col = line.split("\t")
                chrom = col[1]
                position = int(col[2])
                start = position - 1000
                end = position + 1000
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
        fs.close()
    fr.close()
    #end of get genes

def condense_design(disc_genes, condensed):
    '''Create a more condensed file containing only genes and the functions from ensembl.
    This file will contain one instance for every unique gene isntead of the summary which may have
    the same gene printed twice if it is close to multiple SNPs'''
    with open(disc_genes, "r") as fs:
        next(fs)
        with open(condensed, "w") as fc:
            geneid=[]
            annotation=[]
            for line in fs:
                col = line.split("\t")
                gene = col[0]
                designation = col[9]
                geneid.append(gene)
                annotation.append(str(designation).rstrip("\n"))
            geneset = set(zip(geneid, annotation))
            for i in geneset:
                gen = str(i[0])
                anno = str(i[1])
                print("{} :: {}".format(gen, anno), file=fc)
        fc.close()
    fs.close()

def knetapi(condensed, api):
    '''Use the genes from the condensed file to search for Knetminer genome api.'''
    with open(condensed, "r") as fs:
        with open(api, "w") as fj:
            genes = []
            for line in fs:
                col = line.split(" :: ")
                genes.append(col[0])
            genelist = (",").join(genes) #join all iterative elements by ,
            print(genelist)
            pheno = ["coleoptile length", "mesocotyl length", "root length", "seminal root length", "Germination rate", "Seedling growth"]
            #use str.join() to convert multiple elments in a list into one string.
            keyw = "%20OR%20".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
            link = "http://knetminer.rothamsted.ac.uk/riceknet/genome?"
            parameters = {"keyword":keyw, "list":genelist}
            r = requests.get(link, params=parameters)
            #url = "http://knetminer.rothamsted.ac.uk/riceknet/genome?keyword={}&list={}".format(keyw, genelist)
            #print(url)
            #r = requests.get(url)
            r.json()
            r.status_code #check if request is succesfsul.
            print(r.text, file=fj)
        fj.close()
    fs.close()
    return

def parsejs(api, genetab):
    ''' deserialise json into dictionary and extract the genetable which hopefully provide right genes and score given right url'''
    with open(api, "r") as fj:
        decoded = json.load(fj) #deserialise decoded of json, which will be dictionary object.
        #print(type(decoded))
        with open(genetab, "w") as fg:
            print(decoded[u"geneTable"], file=fg) #r.json will put a u infront of the keys of json dictionary
        fg.close()
    fj.close()
    return

def knetsummary(genetab, knet):
    '''Extract the scores only.'''
    with open(genetab, "r") as f:
        next(f)
        with open(knet, "w") as fs:
            for line in f:
                if line == "\n":
                    continue
                col = line.split("\t")
                score=str(col[6]) 
                genes=col[1]
                pheno = ["coleoptile length","mesocotyl length","root length","seminal root length","Germination rate", "Seedling growth"]
                keyw = "+OR+".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
                print(type(keyw))
                #parameters = {"keyword":keyw, "list":genes}
                link="http://knetminer.rothamsted.ac.uk/riceknet/genepage?list={}&keyword={}".format(genes, keyw)
                #r=requests.get(link, params=parameters)
                r=requests.get(link)
                print(r.url)
                print("{}\t{}\t{}".format(genes, score, r.url), file=fs)
        fs.close()
    f.close()
#End of block 7 to print genes, scores and url into scores.txt


def main():
    
    try:
        print("Creating directory for results.")
        mkfolder()
    except:
        raise

    try:
        formated="Formated_results.txt"
        print("writing relevant fields to {}".format(formated))
        formatcsv(formated)
    except:
        raise

    try:
        formated="Formated_results.txt"
        filtered_snps="filtered_snps.txt"
        print("reading from: {}".format(formated))
        print("extracting SNPs exceeding logP threshold of {} into: {}".format(args.p, filtered_snps))
        sigsnps(formated, filtered_snps)
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
        condensed="condensed_genes_designation.txt"
        print("condensing down summary into one occurence for every gene discovered paired with their annotation")
        condense_design(disc_genes, condensed)
    except:
        raise

    try:
        condensed="condensed_genes_designation.txt"
        api="genome.json"
        print("Searching with Knetminer for related genes to genes discovered from Ensembl.")
        knetapi(condensed, api)
    except:
        raise

    try:
        api="genome.json"
        genetab="genetable.txt"
        print("obtaining genetable from Knetminer API")
        parsejs(api, genetab)
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
    args = parser.parse_args()

    main()

    print("The entire pipeline finished at:")
    print(datetime.datetime.now())

    exit



    