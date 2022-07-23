import os
from threading import Timer


TOPICS = {
    'ô tô': [1, 2],
    'ghế công thái học': [1, 2],
    'bàn phím': [1, 2],
    'keycap': [1, 2],
    'quạt để bàn': [1, 2],
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
    try:
        invoke_saver()
    except:
        pass
    try:
        invoke_crawler()
    except:
        pass
    
if __name__ == '__main__':
    # rt = RepeatedTimer(SAVER_DELAY, start_crawling)
    # try:
    #     rt.run()
    # finally:
    #     rt.stop()
    while(True):
        start_crawling()