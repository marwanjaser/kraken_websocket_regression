FROM python:3.7

WORKDIR /ks_testing

RUN pip install pytest
RUN pip install websocket-client
RUN pip install jsonschema

COPY . .

CMD ["cd","ks_testing/src"]

CMD ["pytest","-s","-vv"]