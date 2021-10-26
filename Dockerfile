FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y gettext libgettextpo-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 rwanda
RUN useradd -u 1000 -ms /bin/bash  -g rwanda rwanda

USER rwanda
