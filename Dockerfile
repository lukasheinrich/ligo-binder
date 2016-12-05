FROM andrewosh/binder-base
USER root
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install --yes g++ cpp gcc gfortran git dpkg-dev make binutils libx11-dev libxpm-dev libxft-dev libxext-dev \
                              libssl-dev libpcre3-dev xlibmesa-glu-dev libglew1.5-dev libftgl-dev libmysqlclient-dev \
                              libfftw3-dev graphviz-dev libavahi-compat-libdnssd-dev libldap2-dev python-dev \
                              libxml2-dev libkrb5-dev libgsl0-dev libqt4-dev libx11-dev libxpm-dev
RUN apt-get install -y bzr

RUN pip install pylhe
RUN pip install adage
RUN apt-get install -y graphviz graphviz-dev imagemagick
RUN pip install jsonlines


RUN mkdir /code
RUN chown -R main:main /code

### INSTALL MADGRAPH
USER main
WORKDIR /code
RUN bzr branch lp:~maddevelopers/mg5amcnlo/2.3.3 madgraph-2.3.3

ENV PATH /code/madgraph-2.3.3/bin:$PATH

ADD yadage_widget.py yadage_widget.py
ADD manualui.py manualui.py

USER root
RUN apt-get install -y autoconf
RUN pip install -I --upgrade setuptools
RUN pip install yadage
RUN pip install --upgrade ipywidgets
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension

USER main
