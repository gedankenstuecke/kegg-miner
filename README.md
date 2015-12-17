# KEGG miner
Unfortunately *KEGG* does not offer free access to their FTP any longer. Instead you would now need a subscription to access the data. If you still would like to access and use their data you could just scrape it from their website. For my own research I was interested in the annotations for all the KEGG genomes (~4000 at this point).

Thankfully the URL structure of their website is pretty simple, so you can easily request those pages automatically. The script *kegg-parsers.py* does just this: It first gets the list of all organisms, then it proceeds to get all gene identifiers and downloads the individual gene html-pages. Those can then be processed using BeautifulSoup as well.

## there could be some fancy political statement here
like, information wants to be free or so, you know. 
