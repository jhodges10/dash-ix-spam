FROM ubuntu:18.04
RUN apt-get update && apt-get -y upgrade && rm -fr /var/cache/apt/*

WORKDIR /dashcore

COPY ./dashcore-0.14.0/ /dashcore/
COPY ./dash.conf /dashcore/dash.conf

EXPOSE 9999 9998 29998 19999 19998

CMD ["/dashcore/bin/dashd", "-conf=/dashcore/dash.conf", "-datadir=/data"]
