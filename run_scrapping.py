from function import *
import argparse
import datetime
import pandas as pd
from tqdm import tqdm


def main():
    default_file = str(datetime.date.today().strftime("%b-%d-%Y")).lower() + '.csv'
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', type= str, help= 'search key for the items that we gonna crawl')
    parser.add_argument('--page_start', type= int, default= 1,help= 'page start')
    parser.add_argument('--page_end', type= int, default= 1, help= 'page end')
    parser.add_argument('--result_file_name', type= str, default= default_file , help= 'result file name')
    parser.add_argument('--save_urls', type = bool, default= False, help = 'save urls')
    args = parser.parse_args()
    driver = init_driver()
    item_urls = get_items_from_search(driver, args.key, args.page_start, args.page_end, args.save_urls)
    print(f'Found {len(item_urls)} items!')
    print('Getting reviews...')
    result = []
    try:
        for item in tqdm(item_urls):
            try:
                new_reviews = get_reviews_from_item(driver, item)
            except:
                continue
            else:
                result.append(new_reviews)
    except KeyboardInterrupt:
        print('Interrupted!')
    
    final_result = pd.concat(result)
    print(f'{final_result.shape[0]} reviews have been crawled!')
    
    if not args.result_file_name.endswith('.csv'):
        args.result_file_name = args.result_file_name + '.csv'
    args.result_file_name = args.result_file_name.replace('.csv', '_' +  args.key + '.csv')
    final_result.to_csv(args.result_file_name, index= False)
    
if __name__ == '__main__':
    main()