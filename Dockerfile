FROM cern/cc7-base
ADD . /recast_backend
WORKDIR /recast_backend
RUN yum install -y gcc python-devel openssh-server openssh-clients
RUN curl https://bootstrap.pypa.io/get-pip.py | python -
RUN pip install . --process-dependency-links
