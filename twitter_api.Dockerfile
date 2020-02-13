ARG VERSION=3.8.1-alpine
FROM python:${VERSION} AS twitter_api

# additional package for pip
RUN pip install \
    'tweepy==3.8.0' \
    'mysql-connector-python==8.0.19'
