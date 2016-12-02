FROM andrewosh/binder-base
MAINTAINER Lukas Heinrich <lukas.heinrich@cern.ch>

USER root
RUN apt-get update
RUN apt-get install -y build-essential

