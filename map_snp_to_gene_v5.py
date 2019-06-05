#!/usr/bin/python

#bring python3 print() into python2
from __future__ import print_function
import os, math, traceback, datetime, requests, json, argparse, shutil

def mkfolder():
    '''Create a folder for each gapit results, copy result.csv and reference into that directory.
    All results will then be generated within it. The main function will take the script back into parent.'''
    #folder = str(args.f)[:-4] + str(args.r)[:5]
    folder = str(args.f)[6:-4] + str(args.r)[:4]
    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.mkdir(folder)
        shutil.copy(args.f, folder)
        shutil.copy(args.r, folder)
        os.chdir(folder)
    elif not os.path.exists(folder):
        os.mkdir(folder)
        shutil.copy(args.f, folder)
        shutil.copy(args.r, folder)
        os.chdir(folder)
    #end of mkfolder

def formatcsv(filter):
    with open(args.f) as fres:
        next(fres)
        with open(filter, "w") as flt:
            snp = 0
            print("{}\t{}\t{}\t{}\t{}".format("SNPnum","CHR","snpBP","P","logP"), file=flt)
            for line in fres:
                snp += 1
                col = line.split(",")
                chro = col[1]
                bp = col[2]
                pval = float(col[3])
                logP = -math.log10(pval)
                print("{}\t{}\t{}\t{}\t{}".format(snp,chro,bp,pval,logP), file=flt)
        flt.close()
    fres.close()
    return
#End of block1

def getsnps(filter, threshfile):
    with open(filter) as flt:
        next(flt)
        logP_threshold = args.p
        with open(threshfile, "w") as fthresh:
            print("SNPnum\tCHR\tsnpBP\tP\tlogP", file=fthresh)
            for line in flt:
                col = line.split("\t")
                snp = col[0]
                chr_snp = int(col[1])
                bp_snp = int(col[2])
                pval = float(col[3])
                logP = float(col[4])
                if logP > logP_threshold:
                    print("{}\t{}\t{}\t{}\t{}".format(snp,chr_snp,bp_snp,pval,logP), file=fthresh)
        fthresh.close()
    flt.close()
    return
#End of block2
  
def findCloseGene(chr_snp, bp_snp):
    annotation = args.r
    #annotation = "Os_Nipponbare_IRGSP_1_gene_Loci_and_designation.txt"
    max_distance = 1000
    with open(annotation) as f:
        next(f)
        for line in f:
            col = line.split("\t")
            try:
                chr_gene = int(col[1])
                acc = col[0]
                #chr_gene = int(col[1])
                beg_gene = int(col[2])
                end_gene = int(col[3])
                design = col[4]
                #score = float(col[6])
                #SNP is within gene
                if (chr_snp == chr_gene) & (bp_snp > beg_gene) & (bp_snp < end_gene):
                    #print("Found SNP within gene {}".format(acc)) 
                    return acc
                #SNP is down stream of gene with < max_distance 
                elif (chr_snp == chr_gene) & (abs(bp_snp - beg_gene) < max_distance):
                    #print("Found SNP downstream of {}".format(acc)) 
                    return acc
                #SNP is up stream of gene with < max_distance 
                elif (chr_snp == chr_gene) & (abs(bp_snp - end_gene) < max_distance):
                    #print("Found SNP upstream of {}".format(acc)) 
                    return acc
            except:
                next
        return "FooBar"
    f.close()
#End of block3 to find the genes associated with snps.


def findCloseGeneDesign(chr_snp, bp_snp):
    annotation = args.r
    #annotation = "Os_Nipponbare_IRGSP_1_gene_Loci_and_designation.txt"
    print(os.listdir("."))
    max_distance = 1000
    with open(annotation) as f2:
        next(f2)
        for line in f2:
            col = line.split("\t")
            try:
                chr_gene = int(col[1])
                acc = col[0]
                beg_gene = int(col[2])
                end_gene = int(col[3])
                design = col[4]
                #score = float(col[6])
                #SNP is within gene
                if (chr_snp == chr_gene) & (bp_snp > beg_gene) & (bp_snp < end_gene):
                    #print("Found SNP within gene {}".format(design)) 
                    return design
                #SNP is down stream of gene with < max_distance 
                elif (chr_snp == chr_gene) & (abs(bp_snp - beg_gene) < max_distance):
                    #print("Found SNP downstream of {}".format(design)) 
                    return design
                #SNP is up stream of gene with < max_distance 
                elif (chr_snp == chr_gene) & (abs(bp_snp - end_gene) < max_distance):
                    #print("Found SNP upstream of {}".format(design)) 
                    return design
            except:
                next
        return "FooBar2"
    f2.close()
#End of block3.5 to find the annotation of the genes associated with snps.

def getgdp(threshfile, gdp, genedesign):
    with open(threshfile) as fthresh:
        next(fthresh)
        with open(gdp, "w") as fgdp:
            print("GENE\tCHR\tSNPnum\tsnpBP\tP\tlogP\tdesignation", file=fgdp)
            highlight = []
            highlightdesign = []
            for line in fthresh:
                logP_threshold = args.p
                col = line.split("\t")
                chr_snp = int(col[1])
                snpnum = col[0]
                bp_snp = int(col[2])
                pval = float(col[3])
                logP = float(col[4])
                gene = findCloseGene(chr_snp, bp_snp).replace("LOC_", "")
                design = findCloseGeneDesign(chr_snp, bp_snp)
                blank = "-"
                if gene == "FooBar":
                    print("{}\t{}\t{}\t{}\t{}\t{}".format(blank,blank,blank,blank,blank,blank), file=fgdp)
                else:
                    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(gene,chr_snp,snpnum,bp_snp,pval,logP,design))
                    if logP > logP_threshold:
                        highlight.append(gene)
                        highlightdesign.append(design)
                        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(gene,chr_snp,snpnum,bp_snp,pval,logP,design), file=fgdp)
                    else:
                        print("{}\t{}\t{}\t{}\t{}\t{}".format(snp,chr_snp,snpnum,bp_snp,pval,logP), file=fgdp)
            with open(genedesign, "w") as gd:
                genedesign=zip(highlight, highlightdesign)
                geneset = set(genedesign)
                for i in geneset:
                    gene = str(i[0])
                    funct = str(i[1]).replace("\n", "")
                    print("{} :: {}".format(gene, funct), file=gd)
            gd.close()        
        fgdp.close()
    fthresh.close()
    return
#End of block4 to produce the summary.


def getgs(genedesign):
    """Open gene list and use them to search Knetminer along with keywords"""
    with open(genedesign, "r") as gk:
        with open("genome.json", "w") as af:
            genes = []
            for line in gk:
                col = line.split(" :: ")
                genes.append(col[0])
            genelist = (",").join(genes) #join all iterative elements by ,
            #print(genelist)
            pheno = ["coleoptile length", "mesocotyl length", "root length", "seminal root length", "Germination rate", "Seedling growth"]
            #use str.join() to convert multiple elments in a list into one string.
            keyw = "%20OR%20".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
            url = "http://knetminer.rothamsted.ac.uk/riceknet/genome?keyword={}&list={}".format(keyw, genelist)
            print(url)
            r = requests.get(url)
            r.json()
            r.status_code #check if request is successful.
            print(r.text, file=af)
        af.close()
    gk.close()
    return

def parsejs(genetable):
    """ deserialise json into dictionary and extract the genetable which hopefully provide right genes and score given right url"""
    with open("genome.json", "r") as jf:
        content = json.load(jf) #deserialise content of json, which will be dictionary object.
        #print(type(content))
        with open(genetable, "w") as g:
            print(content[u"geneTable"], file=g) #r.json will put a u infront of the keys of json dictionary
        g.close()
    jf.close()
    return

def gene_score(genetable, scores):
    """Extract the scores only."""
    with open(genetable, "r") as f:
        next(f)
        with open(scores, "w") as sf:
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
                print("{}\t{}\t{}".format(genes, score, r.url), file=sf)
        sf.close()
    f.close()
#End of block 7 to print genes, scores and url into scores.txt

def main():
    try:
        print("Creating directory for results.")
        mkfolder()
        print("moved data to directory.")
    except Exception:
        traceback.print_exc()

    #1) Truncate results file and order by snps.
    filter = "Results_filtered.txt"
    print("taking inputs from gwas results")
    print("writing outputs to:{}".format(filter))      
    try:
        formatcsv(filter)
        print("finished extracting from results")
    except Exception:
        traceback.print_exc()

    #2) Obtain SNPs less than e-6 in p-value
    threshfile = "Results_filtered_threshold.txt"
    print("reading from: {}".format(filter))
    print("extracting SNPS above threshold into: {}".format(threshfile))
    try:
        getsnps(filter, threshfile)
        print("finished extracting snps from: {}".format(threshfile))
    except Exception:
        traceback.print_exc()

    
    #3) define annotation file for findCloseGenes(genes) and findCloseGeneDesign(annotation)
    #annotation = "Os_Nipponbare_IRGSP_1_gene_Loci_and_designation.txt"

    
    #4) Obtain a file summarising the information.
    gdp = "Results_filtered_gdp_FINAL.txt"
    genedesign = "Results_filtered_gene_and_designation.txt"
    print("producing summary of genes associated with significant SNPs")
    print("producing a file of genes associated with significant SNPs and annotations")
    try:
        getgdp(threshfile, gdp, genedesign)
        print("files produced")
    except Exception:
        traceback.print_exc()

    #5) Download json api from Knetminer
    genedesign = "Results_filtered_gene_and_designation.txt"
    try:
        getgs(genedesign)
        print("Obtaining api from knetminer")
    except Exception:
        traceback.print_exc()
    
    #6) Extract gene table from Knetminer
    genetable="genetable.txt"
    try:
        parsejs(genetable)
        print("Extracting genetable from api with scores")
    except Exception:
        traceback.print_exc()

    #7) Compare genetable with genetable and extract only genes + scores
    genetable="genetable.txt"
    scores="scores.txt"
    try:
        gene_score(genetable, scores)
        print("Extracting genes and score from Knetminer")
    except Exception:
        traceback.print_exc()
    
    os.chdir("..")


if __name__ == "__main__":
    #0) defining parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="name of .csv output from GAPIT gwas tool")
    parser.add_argument("-p", help="integer value of logP threshold (-log10 of pvalue) for SNPs", type=int)
    parser.add_argument("-r", help="a reference of genes, location and function provided by IRRI in .txt")
    args = parser.parse_args()

    
    main()
    

print("The entire pipeline completed")
print(datetime.datetime.now())