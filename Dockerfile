FROM ubuntu:18.04

MAINTAINER pacas <pac-pacas@mail.ru>

# Add user
RUN adduser --quiet --disabled-password qtuser

# Install Python 3, PyQt5
RUN apt-get update \
    && apt-get install -y \
      python3 \
      python3-pyqt5