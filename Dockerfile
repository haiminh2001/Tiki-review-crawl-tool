FROM python:3
ENV PATH=$PATH:/webdriver
ENV PATH=$PATH:/usr/lib/jvm/java-11-openjdk-amd64
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
RUN export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
COPY requirements.txt /requirements.txt
COPY run.sh /run.sh
COPY /crawler /crawler
RUN pip install -r requirements.txt
RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list
RUN apt-get update
RUN apt-get install -y --no-install-recommends firefox
RUN mkdir /webdriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux32.tar.gz 
RUN tar -xzf geckodriver-v0.31.0-linux32.tar.gz
RUN mv geckodriver /webdriver
RUN mkdir /crawler/tmpdata
RUN rm geckodriver-v0.31.0-linux32.tar.gz

RUN apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean;
    
# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

COPY libhdfs.so /libhdfs.so
ENV ARROW_LIBHDFS_DIR=/
RUN export ARROW_LIBHDFS_DIR=/

RUN apt install openssh-server openssh-client -y
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.3/hadoop-3.2.3.tar.gz
RUN tar xvzf hadoop-3.2.3.tar.gz
ENV HADOOP_HOME=/hadoop-3.2.3
ENV HADOOP_INSTALL=$HADOOP_HOME
ENV HADOOP_MAPRED_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_HOME=$HADOOP_HOME
ENV HADOOP_HDFS_HOME=$HADOOP_HOME
ENV YARN_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
ENV PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
COPY .bashrc /root/.bashrc
# ENV HADOOP_OPTS"-Djava.library.path=$HADOOP_HOME/lib/nativ"
ENTRYPOINT ["bash", "/run.sh"]