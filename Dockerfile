FROM python:2.7

RUN mkdir /src
WORKDIR /src

ADD . /src/labman_ud

WORKDIR /src/labman_ud
RUN pip install -r requirements.txt

EXPOSE 8000

RUN mkdir /src/labman_ud/labman_ud/media
VOLUME /src/labman_ud/labman_ud/media

ENTRYPOINT ["/src/labman_ud/entrypoint.sh"]