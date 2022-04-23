Crawl reviews từ tiki

### Install requirements

Ubuntu
```bash
pip install -r requirements.txt
webdrivermanager firefox --linkpath /usr/local/bin
```

Window
```bash
pip install -r requirements.txt
webdrivermanager firefox --linkpath /usr/local/bin
```

### Run scrapping
key: Key word để search các sản phẩm trên tiki
page_start: Bắt đầu crawl từ trang thứ bao nhiêu
page_end: Trang cuối cùng 

Ví dụ: đoạn code sau sẽ crawl các sản phẩm máy tính bảng trong 3 trang từ trang 1 đến trang 3
```bash
python run_scrapping.py --key "máy tính bảng" --page_start 1 --page_end 3
```