FROM alpine:3.10

RUN apk update && apk upgrade && apk add --no-cache \
    build-base \
    jpeg-dev \
    poppler-utils \
    python3-dev \
    zlib-dev

RUN pip3 install --upgrade pip && pip3 install \
    black==19.3b0 \
    pdf2image==1.9.0
