FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y gettext libgettextpo-dev

# Git config
RUN git config --global user.email "rwanda@rwanda.com"
RUN git config --global user.name "rwanda"

RUN groupadd -g 1000 rwanda
RUN useradd -u 1000 -ms /bin/bash  -g rwanda rwanda

USER rwanda
