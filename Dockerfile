FROM python

ARG version

RUN apt update && apt install fzf

COPY dist/pubsub-meta-${version}.tar.gz pubsub-meta.tar.gz

RUN pip3 install pubsub-meta.tar.gz
