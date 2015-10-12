FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN useradd --home-dir /home/demo --create-home --shell /bin/bash --uid 1000 demo
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
USER demo
