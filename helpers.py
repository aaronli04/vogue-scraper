import requests
import xml.etree.ElementTree as ET
import concurrent.futures

def get_sitemap(url, ignore):
    urls = []

    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.text

        ns = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        root = ET.fromstring(xml_content)

        for loc_element in root.findall(".//sitemap:loc", namespaces=ns):
            if loc_element is not None:
                if 'hotels' in loc_element.text.lower().strip() or ignore == False:
                    urls.append(loc_element.text)

    return urls

def crawl_sitemap(sitemap_url):
    urls = get_sitemap(sitemap_url, False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:
        links = list(executor.map(lambda url: get_sitemap(url, True), urls))

    return [item for sublist in links for item in sublist]