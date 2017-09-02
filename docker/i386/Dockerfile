FROM i386/debian:wheezy-slim
MAINTAINER Niels AD <docker@nielsd.nl>

WORKDIR /build

RUN \
  apt-get update && \
  apt-get -y install wget libgtk2.0-dev && \
  wget -q http://mirrors.iwi.me/lazarus/releases/Lazarus%20Linux%20i386%20DEB/Lazarus%201.4/fpc_2.6.4-150228_i386.deb && \
  dpkg -i fpc_2.6.4-150228_i386.deb && \
  rm fpc_2.6.4-150228_i386.deb && \
  wget -q http://mirrors.iwi.me/lazarus/releases/Lazarus%20Linux%20i386%20DEB/Lazarus%201.4/fpc-src_2.6.4-150228_i386.deb && \
  dpkg -i fpc-src_2.6.4-150228_i386.deb && \
  rm fpc-src_2.6.4-150228_i386.deb && \
  wget -q http://mirrors.iwi.me/lazarus/releases/Lazarus%20Linux%20i386%20DEB/Lazarus%201.4/lazarus_1.4.0-0_i386.deb && \
  dpkg -i lazarus_1.4.0-0_i386.deb && \
  rm lazarus_1.4.0-0_i386.deb
