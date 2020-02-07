# Base
FROM docker.doku.com/doku-centos7 
#FROM centos:7
USER root

# System dependencies
RUN yum install -y \
        epel-release \
    && yum install -y \
        python3 python3-pip \
        fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
        libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
        curl unzip wget bzip2 \
        xvfb \
    && yum clean all

RUN mkdir -p /apps/ && \
    chown -R 3000:3000 /apps/


# install geckodriver and firefox

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    yum remove firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# install chromedriver and google-chrome

RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

RUN CHROME_SETUP=google-chrome.rpm && \
    wget -O $CHROME_SETUP "https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm" && \
    yum install -y $CHROME_SETUP && \
    rm $CHROME_SETUP


# install phantomjs

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar -jxf phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs && \
    rm phantomjs-2.1.1-linux-x86_64.tar.bz2

#lib for install polygot
RUN yum install -y libicu-devel

# Python libraries
ADD requirements.txt /apps/webcrawler/src/requirements.txt
RUN pip3 install -r /apps/webcrawler/src/requirements.txt

# Source code
COPY . /apps/webcrawler/src/web-crawler
WORKDIR /apps/webcrawler/src/web-crawler

# Network interfaces
EXPOSE 5000

#allow folder app-root
RUN chown -R 3000:3000 /opt/

#allow folder /apps/
RUN chown -R 3000:3000 /apps/

# Run as User 3000
USER 3000

CMD python3 /apps/webcrawler/src/web-crawler/api/api.py