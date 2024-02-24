import requests
from helpers import crawl_sitemap
import pandas as pd
import concurrent.futures

def scrape_vogue():
    sitemap_url = "https://www.vogue.com/sitemap.xml"
    links = crawl_sitemap(sitemap_url)

    print(links)
    
if __name__ == "__main__":
    scrape_vogue()