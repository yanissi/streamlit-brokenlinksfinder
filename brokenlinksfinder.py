import streamlit as st
import base64
import requests
from urllib.parse import urlparse
from usp.tree import sitemap_tree_for_homepage

from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Broken Links Finder",page_icon="🔗",layout="wide")

st.title('Broken Links Finder by Yaniss Illoul from Martech with Me')
st.header("Broken Links Finder")
st.markdown("This interface has been developed by [Yaniss Illoul](https://www.linkedin.com/in/yanissi/) (Feel free to connect!) from [Martech with Me](https://martechwithme.com/?utm_source=brokenlinksfinder&utm_medium=streamlit).")
st.markdown("If you like this project, please consider visiting my website for more Martech tools and tutorials. Don't hesitate to reach out if you have any feature requests or ideas.")

form = st.form(key='brokenLinksFinderForm')

fullDomain = form.text_input("Input Full Website URL (HTTP Protocol Included)",value="")

submit_button = form.form_submit_button(label='Submit')

yourDomain = fullDomain.replace("https://","").replace("http://","").replace("www.","")

# Find and Parse Sitemaps to Create List of all website's pages
def getPagesFromSitemap(fullDomain):

    st.spinner(text="Parsing Sitemap...")

    listPagesRaw = []

    tree = sitemap_tree_for_homepage(fullDomain)
    for page in tree.all_pages():
        listPagesRaw.append(page.url)

    return listPagesRaw


# Go through List Pages Raw output a list of unique pages links
def getListUniquePages(listPagesRaw):

    st.spinner(text="Parsing Sitemap...")

    listPages = []

    for page in listPagesRaw:
        
        if page in listPages:
            
            pass

        else:
            
            listPages.append(page)

    return listPages


# Get External Links List RAW
def ExternalLinkList(listPages):

    st.spinner(text="Identifying External Links...")

    externalLinksListRaw = []

    count = 0
    length_list = len(listPages)

    progressBar = st.progress(100)

    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

    for url in listPages:
        
        count = count + 1/length_list*99
        progressBar.progress(count/100)
        
        request = requests.get(url, headers=user_agent)
        content = request.content
        soup = BeautifulSoup(content, 'lxml')
        
        list_of_links = soup.find_all("a")
        
        for link in list_of_links:

            try:

                if yourDomain in link["href"] or "http" not in link["href"]:

                    pass

                else:

                    externalLinksListRaw.append([url,link["href"],link.text])

            except:

                pass
                
        print(count,"pages checked out of ",length_list,".")

    return externalLinksListRaw


# Get External Links List Unique Values
def getUniqueExternalLinks(externalLinksListRaw):

    uniqueExternalLinks = []

    for link in externalLinksListRaw:
        
        if link[1] in uniqueExternalLinks:
            
            pass

        else:
            
            uniqueExternalLinks.append(link[1])

    return uniqueExternalLinks


# Go through Each Unique Link to Identify Broken Ones
def identifyBrokenLinks(uniqueExternalLinks):

    st.spinner(text="Identifying Broken Links...")

    count = 0
    length_uniqueExternalLinks = len(uniqueExternalLinks)
    progressBar = st.progress(100)
    
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

    brokenLinksList = []

    for link in uniqueExternalLinks:
        
        count = count + 1/length_uniqueExternalLinks*99
        progressBar.progress(count/100)
        
        print("Checking external link #",count," out of ",length_uniqueExternalLinks,".")
        
        try:
        
            statusCode = requests.get(link, headers=user_agent).status_code
            
            if statusCode == 404:
                
                brokenLinksList.append(link)
                
            else:
                
                pass
            
        except:
            
            brokenLinksList.append(link)

    return brokenLinksList


# Identify Unique Broken Links and Matches them to Original List of All External Links
def matchBrokenLinks(brokenLinksList,externalLinksListRaw):

    st.spinner(text="Generating Dataframe...")

    brokenLinkLocation = []

    for link in externalLinksListRaw:
        
        if link[1] in brokenLinksList:
                    
            brokenLinkLocation.append([link[0],link[1],link[2]])
            
        else:
            
            pass

    dataframeFinal = pd.DataFrame(brokenLinkLocation,columns=["URL","Broken Link URL","Anchor Text"])

    return dataframeFinal


if submit_button:

    listPagesRaw = getPagesFromSitemap(fullDomain)
    st.spinner(text="Generating Dataframe...")
    listPages = getListUniquePages(listPagesRaw)
    st.spinner(text="Generating Dataframe...")
    externalLinksListRaw = ExternalLinkList(listPages)
    st.spinner(text="Generating Dataframe...")
    uniqueExternalLinks = getUniqueExternalLinks(externalLinksListRaw)
    st.spinner(text="Generating Dataframe...")
    brokenLinksList = identifyBrokenLinks(uniqueExternalLinks)
    st.spinner(text="Generating Dataframe...")

    st.dataframe(matchBrokenLinks(brokenLinksList,externalLinksListRaw))
    df = matchBrokenLinks(brokenLinksList,externalLinksListRaw)

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    st.markdown('### **⬇️ Download Output as CSV File **')
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as "filename.csv")'
    st.markdown(href, unsafe_allow_html=True)
