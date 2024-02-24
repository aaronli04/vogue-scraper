import requests
from helpers import crawl_sitemap, get_hotel_info
import pandas as pd
import concurrent.futures

def scrape_vogue():
    sitemap_url = "https://www.vogue.com/sitemap.xml"
    links = crawl_sitemap(sitemap_url)

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        nested_results = list(executor.map(get_hotel_info, links))
    
    results = [item for sublist in nested_results for item in sublist]

    df = pd.DataFrame(results)
    df.to_csv('hotel_data.csv', index=False)


if __name__ == "__main__":
    scrape_vogue()