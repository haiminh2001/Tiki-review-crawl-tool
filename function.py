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
STAR_DICT = {
    'Rất không hài lòng' : '1',
    'Không hài lòng' : '2',
    'Bình thường' : '3',
    'Hài lòng': '4',
    'Cực kì hài lòng' : '5',
}
ITEM_LINK_FILE = 'item_links.txt'

def init_driver(headless= True):
    options = Options()
    options.headless = headless
    driver=webdriver.Firefox(options= options)
    return driver

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
                        rating = review.get('reviewRating')
                        content = review.get('reviewBody')
                        if content:
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
        
