ARG PYTHON_VERSION=3.8.1-alpine
FROM python:${PYTHON_VERSION}

# additional package for pip
RUN pip install \
    'tweepy==3.8.0' \
    'mysql-connector-python==8.0.19' \
    'boto3==1.12.7' 