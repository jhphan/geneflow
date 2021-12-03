
# build singularity

FROM golang:1.17.3-alpine3.15 as singularity_builder 

RUN apk update \
    && apk add --no-cache \
        ca-certificates \
        build-base \
        linux-headers \
        git \
        openssl-dev \
        util-linux-dev \
        libseccomp-dev \
        gawk \
    && mkdir -p $GOPATH/src/github.com/apptainer \
    && cd $GOPATH/src/github.com/apptainer \
    && git clone -b v3.8.5 https://github.com/apptainer/singularity.git \
    && cd $GOPATH/src/github.com/apptainer/singularity \
    && ./mconfig -s -S -p /opt/singularity \
    && cd $GOPATH/src/github.com/apptainer/singularity/builddir \
    && make \
    && make install


# build final container

FROM python:3.10.0-alpine3.15

COPY --from=singularity_builder /opt/singularity /opt/singularity

WORKDIR /src
COPY . /src/geneflow

RUN apk update \
    && apk add --no-cache --virtual .build-deps build-base libffi-dev openssl-dev \
    && apk add --no-cache git squashfs-tools libseccomp sudo coreutils \
    && pip install -U pip \
    && pip install ./geneflow \
    && rm -rf /src/* \
    && rm -rf /root/.cache/pip/* \
    && apk del .build-deps
    
ENV PATH /opt/singularity/bin:$PATH
