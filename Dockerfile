FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

RUN pip install -r requirements.txt

RUN groupadd -g 1000 rwanda
RUN useradd -u 1000 -ms /bin/bash  -g rwanda rwanda

USER rwanda
