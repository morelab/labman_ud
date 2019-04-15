FROM alpine

RUN apk add rsync

RUN mkdir /source
RUN mkdir /target

VOLUME /source
VOLUME /target
VOLUME /etc/crontabs/

CMD ["crond", "-f"]
