from selenium  import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from tqdm import tqdm
import json
import requests
# import traceback
from run_scrapping import my_stacktrace

# from urllib.parse import parse_qs, urlparse

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

ITEM_LINK_FILE = 'item_links.txt'

ITEM_FEATURE_COLUMNS = ['Công ty phát hành', 'Ngày xuất bản', 'Kích thước', 'Loại bìa', 'Số trang']

MAX_LOOP = 1000
class my_driver:
    def __enter__(self, headless = True):
        options = Options()
        options.headless = headless
        self.driver=webdriver.Firefox(options= options)
        self.driver.set_page_load_timeout(3)
        self.session = requests.Session()
        self.update_session()

        return self
    
    def update_session(self):
        selenium_user_agent = self.driver.execute_script("return navigator.userAgent;")
        self.session .headers.update({"user-agent": selenium_user_agent})
        for cookie in self.driver.get_cookies():
            self.session .cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    
    def __exit__(self, *args):
        self.driver.quit()
        
    

def simple_process(df):
    if len(df):
        df['rating'] = df['rating'].apply(lambda x: int(x))
    return df

def get_review_page(driver, params):
    driver.update_session()
    res = driver.session.get('https://tiki.vn/api/v2/reviews',  params = params)
    data = None
    status_code = res.status_code
    if status_code == 200:
        data = json.loads(res.content.decode() )
    else: 
        print(params['product_id'], res.status_code)
    return data, status_code



    

def get_review_table(driver, pid, spid):
    review_result = {'review' : [], 'rating' : []}
    # next_button = driver.find_element_by_css_selector('.button .c_button .s_button')
    # while
    item_agg = {'pid': [pid]}
    params = {
        'limit': 20,
        'page': 1,
        'spid': spid,
        'product_id': pid,
        'seller_id': 1,
        'include': 'comments,contribute_info,attribute_vote_summary',
        'sort': 'score|desc,id|desc,stars|all',
        
    }
    data, status_code = get_review_page(driver, params)
    
    reviews, ratings = [], []
    
    if status_code == 200 and data:
        
        item_agg['rating_average'] = [data['rating_average']]
        item_agg['reviews_count'] = [data['reviews_count']]
        
        
        item_reviews = data['data']
        reviews = [r['content'] for r in item_reviews]
        ratings = [r['rating'] for r in item_reviews]
        
        num_left = item_agg['reviews_count'][-1] - len(item_reviews)
        loop_count = 0
        
        get_sth = True
        while num_left and get_sth and loop_count < MAX_LOOP:
            params['page'] = params['page'] + 1
            data, status_code = get_review_page(driver, params)
            get_sth = False
            if data and status_code == 200:
                loop_count += 1
                item_reviews = data['data']
                if len(item_reviews):
                    get_sth = True
                
                    reviews.extend( [r['content'] for r in item_reviews])
                    ratings.extend( [r['rating'] for r in item_reviews])
                    num_left -= len(item_reviews)
            else:
                break

    #remove blank reviews                
    for i, r in enumerate(reviews):
        if len(r):
            review_result['review'].append(r)
            review_result['rating'].append(ratings[i])
    
    
    
    
    
        
    return review_result, item_agg


def get_item_table(driver, item_agg):

    item_result = item_agg 
    

    #detailed information
    
    item_result['item'] = driver.driver.find_element(by= By.CSS_SELECTOR, value = '.title').get_attribute('innerHTML')
    
    try:
        item_result['price'] = int(driver.driver.find_element(by= By.CSS_SELECTOR, value = '.product-price__current-price').get_attribute('innerHTML').replace('.','').split(' ')[0])
    except: 
        try:
            item_result['price'] = int(driver.driver.find_element(by= By.CSS_SELECTOR, value = '.flash-sale-price span').get_attribute('innerHTML').replace('.','').split(' ')[0])  
        except:
            print(my_stacktrace(), end = '' if os.environ['debug'] == 'n' else '\n')
    table = driver.driver.find_element(by= By.CSS_SELECTOR, value = '.content.has-table').find_elements(by= By.CSS_SELECTOR, value = 'td')
    
    keys = [k.get_attribute('innerHTML') for k in table[::2]]
    values = [k.get_attribute('innerHTML') for k in table[1::2]]
    table_features = dict(zip(keys, values))
    for f in ITEM_FEATURE_COLUMNS:
        item_result[f] = table_features.get(f)
    
    return item_result
 

def get_item_data(driver: my_driver, url) -> pd.DataFrame:
    

    driver.driver.get(url)
    spid = int(url.split('spid=')[-1])
    pid = url.split('.html')[0].split('-p')[-1]
    
    review_result, item_agg = get_review_table(driver, pid, spid)

    item_result = get_item_table(driver, item_agg)
    
    return pd.DataFrame(review_result), pd.DataFrame(item_result)



def get_items_from_search(driver: my_driver, search_str: str, page_start= 1, page_end= 1, write_to_file= True) -> list:
    print('Getting item links from tiki..........')
    result = []
    page_end = page_end if page_end >= page_start else page_start
    search_str = search_str.replace(' ', '%20')
    for i in tqdm(range(page_start, page_end + 1)):
        page = '' if i == 1 else f'&page={i}'        
        try:
            driver.driver.get('https://tiki.vn/search?q=' + search_str + page )
            try:
                WebDriverWait(driver.driver,10).until(lambda driver: not driver.title.startswith('giá'))
            except:
                continue
            driver.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(driver.driver,10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.product-item")))
            except:
                print(my_stacktrace(), end = '' if os.environ['debug'] == 'n' else '\n')
                    
            items = driver.driver.find_elements(by= By.CSS_SELECTOR, value=  "a.product-item")
            
            for item in items:
                try:
                    link = item.get_attribute('href')
                    if link.startswith('https://tiki.vn'):
                        result.append(link)
                except:
                    print(my_stacktrace(), end = '' if os.environ['debug'] == 'n' else '\n')
                    continue
        except:
            
            print(my_stacktrace(), end = '' if os.environ['debug'] == 'n' else '\n')
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
        
