import requests
import xml.etree.ElementTree as ET
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Get sitemap from website
def get_sitemap(url, ignore):
    urls = []

    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.text

        ns = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        root = ET.fromstring(xml_content)

        for loc_element in root.findall(".//sitemap:loc", namespaces=ns):
            if loc_element is not None:
                if ('best' in loc_element.text.lower().strip() and 'hotels' in loc_element.text.lower().strip()) or ignore == False:
                    urls.append(loc_element.text)

    return urls

# Get all relevant links from sitemap
def crawl_sitemap(sitemap_url):
    urls = get_sitemap(sitemap_url, False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:
        links = list(executor.map(lambda url: get_sitemap(url, True), urls))

    return [item for sublist in links for item in sublist]

# Function to extract soup from a webpage using Selenium
def extract_soup_with_selenium(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    driver.implicitly_wait(2)

    try:
        # Wait for the reviews element to be present
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except TimeoutException:
        print("Timed out waiting for reviews element.")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    finally:
        driver.quit()
    
def get_hotel_info(link):
    results = []

    soup = extract_soup_with_selenium(link)
    container_elements = soup.find_all('div', class_='body__inner-container')
    if container_elements:
        for container_element in container_elements:
            name = ''
            description = ''
            amenities = ''
            address = ''
            link = ''
            
            name_element = container_element.find('div', {'role': 'heading'})
            if name_element:
                name = name_element.text.strip()
            else:
                name_element = container_element.find('h2')
                if name_element:
                    name = name_element.text.strip()

            description_elements = container_element.find_all('p')
            for description_element in description_elements:
                if description_element:
                    description_text = description_element.text.strip()
                    if '—' in description_text or name in description_text:
                        description = description_text
                        # Search for link in description text
                        outbound_link = description_element.find('a', class_='external-link')
                        if outbound_link:
                            link = outbound_link['href']
                    elif 'Amenities:' in description_text:
                        amenities = description_text.replace('Amenities:', '').strip()
                    elif 'Address:' in description_text or 'Location:' in description_text:
                        address = description_text.replace('Address:', '').strip()
                        address = description_text.replace('Location:', '').strip()
            
            if any([name, link, description, amenities, address]):
                results.append([name, link, description, amenities, address]) 
                
    return results