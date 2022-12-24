from function import *
import argparse
import datetime
import pandas as pd
from tqdm import tqdm
from traceback import format_exc

if os.environ['debug'] == 'y':
    import warnings
    warnings.filterwarnings("ignore")

my_stacktrace = format_exc if os.environ['debug']  == 'y' else lambda : ''
def main():
    global my_stacktrace
    default_file = str(datetime.date.today().strftime("%b-%d-%Y")).lower() 
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', type= str, help= 'search key for the items that we gonna crawl')
    parser.add_argument('--page_start', type= int, default= 1,help= 'page start')
    parser.add_argument('--page_end', type= int, default= 1, help= 'page end')
    parser.add_argument('--result_file_name', type= str, default= default_file , help= 'result file name')
    parser.add_argument('--save_urls', action = 'store_true', help = 'save urls')
    parser.add_argument('--compress', action = 'store_true', help= 'parquet or csv')
    parser.add_argument('--debug', action = 'store_true', help= 'log bug')
    args = parser.parse_args()
            
    file_type = '.parquet.gzip' if args.compress else '.csv'
    if not args.result_file_name.endswith(file_type):
        args.result_file_name = args.result_file_name + file_type
    
    
 
        
        
    with my_driver() as driver:
        item_urls = get_items_from_search(driver, args.key, args.page_start, args.page_end, args.save_urls)
        print(f'Found {len(item_urls)} items!')
        print('Getting reviews...')
        result = []
        item_result = []
        # get_item_data(driver, item_urls[0])
        try:
            for item in tqdm(item_urls):
                try:
                    new_reviews, new_item = get_item_data(driver, item)
                except:
                    print(my_stacktrace(), end = '' if os.environ['debug'] == 'n' else '\n')
                    continue
                else:
                    result.append(new_reviews)
                    item_result.append(new_item)
        except KeyboardInterrupt:
            print('Interrupted!')
            
    final_result = simple_process(pd.concat(result) if len(result) else pd.DataFrame([]))
    item_result = pd.concat(item_result ) if len(result) else pd.DataFrame([])
    print(f'{final_result.shape[0]} reviews have been crawled!')
    if len(final_result) + len(item_result):
        if item_result.shape[0]:
            item_result['category'] = [args.key for _ in range(item_result.shape[0])]
        
        
        to_file = 'to_parquet'  if args.compress else 'to_csv'
        while os.path.exists('/crawler/tmpdata/' + args.result_file_name):
            args.result_file_name  = args.result_file_name.split(file_type)[0] + '(1)' + file_type
            
        while os.path.exists('/crawler/tmpdata_item/' + args.result_file_name):
            args.result_file_name  = args.result_file_name.split(file_type)[0] + '(1)' + file_type
            
        getattr(final_result, to_file)('/crawler/tmpdata/' + args.result_file_name, index = False)
        getattr(item_result, to_file)('/crawler/tmpdata_item/' + args.result_file_name, index = False)

if __name__ == '__main__':
    main()