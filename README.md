Crawl reviews từ tiki

### Install requirements

```bash
git clone https://github.com/haiminh2001/Tiki-review-crawl-tool.git
cd Tiki-review-crawl-tool
#build docker image
docker build -t crawler . 
```
Chạy docker
```bash
#start docker
docker run -v  $PWD/crawler:/crawler -it crawler /bin/bash
cd crawler
#start crawling
python coordinator.py
```

#Test purpose

### Run scrapping
--key: Key word để search các sản phẩm trên tiki

--page_start: Bắt đầu crawl từ trang thứ bao nhiêu

--page_end: Trang cuối cùng 

Ví dụ: đoạn code sau sẽ crawl các sản phẩm máy tính bảng trong 3 trang từ trang 1 đến trang 3
```bash
python run_scrapping.py --key "máy tính bảng" --page_start 1 --page_end 3
```
Các tham số khác

--result_file_name : Tên file csv kết quả

--save_urls : True/False nếu True thì sẽ lưu ra file link url của các sản phẩm tìm được, mặc định là không lưu
