FROM i386/debian:wheezy-slim
MAINTAINER Niels AD <docker@nielsd.nl>

WORKDIR /build

ENV mirror  https://downloads.sourceforge.net/project/lazarus/Lazarus%20Linux%20i386%20DEB/Lazarus%201.4
ENV fpc     fpc_2.6.4-150228_i386.deb
ENV fpc_src fpc-src_2.6.4-150228_i386.deb
ENV lazarus lazarus_1.4.0-0_i386.deb

RUN \
  apt-get update && \
  apt-get -y --no-install-recommends install \
    wget \
    ca-certificates \
    binutils \
    gcc \
    libgtk2.0-dev

RUN for pkg in "${fpc}" "${fpc_src}" "${lazarus}"; do \
    wget -q ${mirror}/${pkg} && \
    dpkg -i ./${pkg} && \
    rm ./${pkg}; \
  done

RUN \
  apt-get -y -f install && \
  apt-get purge -y wget && \
  apt-get clean -y && \
  apt-get autoclean -y && \
  apt-get autoremove -y && \
  rm -rf /var/cache/debconf/*-old && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /usr/share/doc/* && \
  rm -rf /tmp/* && \
  rm -rf /var/tmp/*
