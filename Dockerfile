FROM python:2.7
ADD . /code
WORKDIR /code
RUN pip install . --process-dependency-links
