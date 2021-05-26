FROM python:3.8-slim-buster

ARG DEBIAN_FRONTED=noninteractive

WORKDIR /app
COPY ./requirements/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY shortlink shortlink
WORKDIR /app/shortlink

ENTRYPOINT [ "python3" ]
CMD [ "-m" , "flask", "run", "--host=0.0.0.0" ]
