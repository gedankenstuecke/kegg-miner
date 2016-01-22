from bs4 import BeautifulSoup
import sys
import requests
import os
import re
import time

# some general setup here
# organism-link: the page that lists all KEGG genomes available
organism_link = "http://www.genome.jp/kegg/catalog/org_list.html"
# genelist_link: The base-link which lists all genes for a single organism
genelist_link = "http://www.genome.jp/dbget-bin/get_linkdb?-t+genes+genome:"
# gene_link: the link that will display information for a single gene.
gene_link = "http://www.genome.jp/dbget-bin/www_bget?"
# where should the stuff be saved?
outputdir = "KEGG_results"

def get_organisms(link,output):
    '''
    get the taxon IDs of KEGG from the organism_link
    page. Don't scrape if the data is already there.

    If we have to parse the data we also dump it, so
    we don't have to do it twice.
    '''
    taxon_ids = []
    # check whether all the files are already there
    if output[-1] != "/":
        output += "/"
    if not os.path.isdir(output):
        os.makedirs(output)
    # awesome, the file already exists, so we just have to parse
    # the local file!
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
        retries = 0
        # ok, let's start to look for the taxon files
        # do we have the gene list already? great, we
        # just parse it and we're good to go.
        if not os.path.isdir(output+taxon):
            os.makedirs(output+taxon)
        if os.path.exists(output+taxon+"/geneids.txt"):
            for i in open(output+taxon+"/geneids.txt"):
                geneids.append(i.strip())
        # nope, no files here yet, so we get the list from KEGG.
        else:
            while geneids == [] and retries < 500:
                time.sleep(20)
                print "genelist\t" + taxon + "\t" + str(retries)
                geneids = get_genelist(taxon)
                retries += 1
            outfile = open(output+taxon+"/geneids.txt","w")
            # let's write the gene-IDs to a file so we don't hit
            # KEGG for a second time
            for i in geneids:
                outfile.write(i+"\n")
            outfile.close()
        # now we can go and grab those gene files, one by one!
        for i in geneids:
            get_singlegene(taxon,i,output)
            time.sleep(0.1)


def get_genelist(taxon):
    '''
    This just gets the complete list of gene-IDs for
    a single species and returns the IDs as a list.
    '''
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
    # let's see whether we have this gene already on our HDD/SSD
    # if not: let's grab it from KEGG
    # we're not doing any parsing here, to keep things up to speed
    if not os.path.exists(output+taxon+"/"+gene_name+".txt"):
        print "download\t" + taxon + "\t" + gene_name
        url = gene_link + gene_name
        response = requests.get(url)
        outfile = open(output+taxon+"/"+gene_name+".txt","w")
        outfile.write(response.content)
        outfile.close()

def main():
    taxon_ids = get_organisms(organism_link,outputdir)
    print taxon_ids
    iterate_taxa(taxon_ids,outputdir)
    print "DONE"

if __name__ == "__main__":
    main()
