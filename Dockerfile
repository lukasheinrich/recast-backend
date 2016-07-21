FROM cern/cc7-base
ADD . /recast_backend
WORKDIR /recast_backend
RUN yum install -y gcc gcc-c++ graphviz-devel ImageMagick python-devel libffi-devel openssl openssl-devel unzip nano autoconf automake libtool openssh-server openssh-clients
RUN curl https://bootstrap.pypa.io/get-pip.py | python -
RUN pip install . --process-dependency-links
