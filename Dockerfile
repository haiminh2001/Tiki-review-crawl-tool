FROM python:3
ENV PATH=$PATH:/webdriver
COPY requirements.txt /requirements.txt
COPY /crawler /crawler
RUN pip install -r requirements.txt
RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list
RUN apt-get update
RUN apt-get install -y --no-install-recommends firefox
RUN mkdir /webdriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux32.tar.gz 
RUN tar -xzf geckodriver-v0.31.0-linux32.tar.gz
RUN mv geckodriver /webdriver
RUN mkdir /webdriver/tmpdata
RUN rm geckodriver-v0.31.0-linux32.tar.gz
