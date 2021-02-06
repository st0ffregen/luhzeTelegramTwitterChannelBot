FROM python:3
WORKDIR /usr/src/app
COPY . .
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install tweepy
RUN pip3 install feedparser
RUN pip3 install python-dotenv
RUN pip3 install python-telegram-bot --upgrade
CMD ["python", "/usr/src/app/main.py"]