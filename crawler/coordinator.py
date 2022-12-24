import os
from threading import Timer
import argparse

TOPICS = {
    'sách': [1, 2],
    'sách tiếng việt': [1, 2],
    'sách kĩ năng sống': [1, 2],
    'sách tiếng anh': [1, 2],
    'sách nhật bản': [1, 2],
    'sách tư duy': [1,2],
    'sách văn học': [1,2],
    'sách kinh tế': [1,2],
    'sách tiểu thuyết': [1,2],
    'truyện tranh': [1,2],
    'sách giáo khoa': [1,2],
    'sách chính trị': [1,2],
    'sách thiếu nhi': [1,2],
}

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self.run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

SAVER_DELAY = 0.5 * 3600

def invoke_saver():
    os.system('python /crawler/saver.py') 

def invoke_crawler():
    for topic in TOPICS.keys():
        os.system(f'python /crawler/run_scrapping.py --key "{topic}" --page_start {TOPICS[topic][0]} --page_end {TOPICS[topic][1]}') 

def start_crawling():
    # try:
    #     invoke_saver()
    # except:
    #     pass
    try:
        try:
            invoke_crawler()
        except KeyboardInterrupt:
            return False
    except:
        return False
    return True
    
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--debug', action = 'store_true', help= 'log bug')
    args = parser.parse_args()
    os.environ['debug'] = 'y' if args.debug else 'n'


    while(start_crawling()):
        pass