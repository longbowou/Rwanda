FROM python:3.9

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y gettext libgettextpo-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 app
RUN useradd -u 1000 -ms /bin/bash  -g app app

USER app