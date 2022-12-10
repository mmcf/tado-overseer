FROM python:3.10-slim

WORKDIR /src
ENV PYTHONPATH=/src

COPY requirements.txt /src/requirements.txt

RUN pip install -U pip
RUN pip install --user -r requirements.txt

COPY tado/ tado/
COPY config.yaml .

ENTRYPOINT [ "python" ]
