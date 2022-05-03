from multiprocessing.connection import Client
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from tqdm import tqdm
import json
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

ITEM_LINK_FILE = 'item_links.txt'

def init_driver(headless= True):
    options = Options()
    options.headless = headless
    driver=webdriver.Firefox(options= options)
    return driver

def simple_process(df):
  df = df.groupby('review').mean()
  df['rating'] = df['rating'].apply(lambda x: int(x))
  return df.reset_index()

def get_reviews_from_item(driver: webdriver.Firefox, url) -> pd.DataFrame:
    result = {'review' : [], 'rating' : []}
    driver.get(url)
    elems = driver.find_elements(by= By.TAG_NAME, value = 'script')
    for elem in elems:
        try:
            jsonData = json.loads(elem.get_attribute('innerHTML'))
            graph = jsonData.get('@graph')
            if graph:
                reviews = graph[0].get('review')
                if reviews:
                    for review in reviews:
                        content = review.get('reviewBody')
                        if content:
                            rating = review.get('reviewRating')
                            result['review'].append(content)
                            result['rating'].append(int(rating.get('ratingValue')))
                 
                break
                   
        except: 
            pass
      
    return pd.DataFrame(result)


def get_items_from_search(driver, search_str: str, page_start= 1, page_end= 1, write_to_file= True) -> list:
    print('Getting item links from tiki..........')
    result = []
    page_end = page_end if page_end >= page_start else page_start
    search_str = search_str.replace(' ', '%20')
    for i in tqdm(range(page_start, page_end + 1)):
        page = '' if i == 1 else f'&page={i}'        
        try:
            driver.get('https://tiki.vn/search?q=' + search_str + page )
            try:
                WebDriverWait(driver,10).until(lambda driver: not driver.title.startswith('giá'))
            except:
                continue
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(driver,10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.product-item")))
            except:
                pass
            items = driver.find_elements(by= By.CSS_SELECTOR, value=  "a.product-item")
            
            for item in items:
                link = item.get_attribute('href')
                if link.startswith('https://tiki.vn'):
                    result.append(link)
        except:
            continue
        if write_to_file:
            write_links_to_file(result)
    return result

def write_links_to_file(links: list):
    start = '\n' if is_non_zero_file(ITEM_LINK_FILE) else ''
    with open(file = ITEM_LINK_FILE, mode = 'a', encoding= 'utf-8') as f:
        f.write(start)
        last = links.pop(-1)
        for link in links:
            f.write(link + '\n')
        f.write(last)
        f.close()
     
from bs4 import BeautifulSoup
import requests   
b = "https://www.lazada.vn/products/hcmkem-tay-long-huyen-phi-tang-serum-triet-long-vinh-vien-triet-long-chan-long-tay-long-bikini-ria-mep-an-toan-tien-loi-chi-phi-re-i727420418-s2254120734.html?spm=a2o4n.home.just4u.4.612ee182fwKLVk&&scm=1007.17519.162103.0&pvid=cdd76bd1-1a85-4401-a96e-e6ffd6ac7fea&search=0&clickTrackInfo=tctags%3A866654242+1880304801+542830244+524257886+830083863+115545340+1215065286+1498575426%3Btcsceneid%3AHPJFY%3Bbuyernid%3A32aaefc6-4a11-471e-87c6-4031e2292b45%3Btcboost%3A0%3Bpvid%3Acdd76bd1-1a85-4401-a96e-e6ffd6ac7fea%3Bchannel_id%3A0000%3Bmt%3Ahot%3Bitem_id%3A727420418%3Bself_ab_id%3A162103%3Bself_app_id%3A7519%3Blayer_buckets%3A955.7332_5437.25236_6059.28891_955.3631%3Bpos%3A3%3B"
def get_reviews_from_lazada_item(url):
    result = {'review' : [], 'rating' : []}
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    with open('buffer.cache', 'w') as f:
        
        scripts = soup.find_all('script')
        for script in scripts:
            if '__moduleData__' in script.text:
                f.write(script.text)
        f.close()

    with open('buffer.cache', 'r') as f:
        for line in f:
            if line.startswith('    var __moduleData__ = '):
                data = line.strip()
                data = data.replace('var __moduleData__ = ','')
                data = data[: - 1]
                try:
                    data = json.loads(data).get('data').get('root').get('fields').get('review')
                except:
                    break
                reviews = data.get('reviews')
                for review in reviews:
                    content = review.get('reviewContent')
                    if content:
                        result['review'].append(content)
                        result['rating'].append(review.get('rating'))
                break
        f.close()
    return pd.DataFrame(result)

print(get_reviews_from_lazada_item(b))

# print(load_url_selenium_lazada(a))

c = "https://my.lazada.vn/pdp/review/getReviewList?itemId=294344744&pageSize=5&filter=0&sort=0&pageNo=3"
import http.client
connection = http.client.HTTPSConnection('www.lazada.vn')
connection.request('GET', c)
response = connection.getresponse()
print(response.read().decode())