from bs4 import BeautifulSoup
import sys
import requests
import os
import re
import time

# some general setup here
organism_link = "http://www.genome.jp/kegg/catalog/org_list.html"
genelist_link = "http://www.genome.jp/dbget-bin/get_linkdb?-t+genes+genome:"
gene_link = "http://www.genome.jp/dbget-bin/www_bget?"
outputdir = "KEGG_results"

def get_organisms(link,output):
    '''
    get the taxon IDs of KEGG from the organism_link
    page. Don't scrape if the data is already there.
    '''
    taxon_ids = []
    # check whether all the files are already there
    if output[-1] != "/":
        output += "/"
    if not os.path.isdir(output):
        os.makedirs(output)
    if os.path.exists(output+"taxon_ids.txt"):
        for i in open(output+"taxon_ids.txt"):
            taxon_ids.append(i.strip().split("\t")[0])
        return taxon_ids

    # ok, we have to get the list again. let's do this!
    response = requests.get(link)
    soup = BeautifulSoup(response.content,"html5lib")
    taxon_ahrefs = soup.find_all("a",href=re.compile("\?T"))
    taxon_outhandle = open(output+"taxon_ids.txt","w")
    for href in taxon_ahrefs:
        tid = href["href"].split("?")[-1]
        tname = href.text
        taxon_ids.append(tid)
        taxon_outhandle.write(tid+"\t"+tname+"\n")
    taxon_outhandle.close()
    return taxon_ids

def iterate_taxa(taxon_ids,output):
    '''
    iterate over the taxon-list we got from
    get_organisms and try to grab the list of all genes
    if it's not already on our harddrive
    '''
    if output[-1] != "/":
        output += "/"
    for taxon in taxon_ids:
        geneids = []
        if not os.path.isdir(output+taxon):
            os.makedirs(output+taxon)
        if os.path.exists(output+taxon+"/geneids.txt"):
            for i in open(output+taxon+"/geneids.txt"):
                geneids.append(i.strip())
        else:
            outfile = open(output+taxon+"/geneids.txt","w")
            geneids = get_genelist(taxon)
            for i in geneids:
                outfile.write(i+"\n")
            outfile.close()
            for i in geneids:
                get_singlegene(taxon,i,output)
                time.sleep(0.1)


def get_genelist(taxon):
    url = genelist_link + taxon
    response = requests.get(url)
    soup = BeautifulSoup(response.content,"html5lib")
    geneids = []
    links = soup.find_all("a",href=re.compile("www_bget\?"))
    for link in links:
        gid = link["href"].split("?")[-1]
        geneids.append(gid)
    return geneids

def get_singlegene(taxon,gene_name,output):
    if not os.path.exists(output+taxon+"/"+gene_name+".txt"):
        print "download\t" + taxon + "\t" + gene_name
        outfile = open(output+taxon+"/"+gene_name+".txt","w")
        url = gene_link + gene_name
        response = requests.get(url)
        outfile.write(response.content)
        outfile.close()

def main():
    taxon_ids = get_organisms(organism_link,outputdir)
    print taxon_ids
    iterate_taxa(taxon_ids,outputdir)

if __name__ == "__main__":
    main()
