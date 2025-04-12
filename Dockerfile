FROM python:3.9

WORKDIR /code

COPY ./src-api/ /code/

RUN curl --output /code/kevlar-test.tar.gz https://dh.fbk.eu/software/kevlar-test.tar.gz
RUN tar xzf /code/kevlar-test.tar.gz

ARG LANGS

RUN apt-get update
RUN apt-get install -y jq
RUN chmod u+x install.sh
RUN ./install.sh $LANGS

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


CMD ["uvicorn", "server:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
