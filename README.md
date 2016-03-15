# recast-backend
[![Build Status](https://travis-ci.org/recast-hep/recast-backend.svg?branch=master)](https://travis-ci.org/recast-hep/recast-backend)


The modules provided by this package provide the glue between the [RECAST Control Center](https://github.com/recast-hep/recast-control-center-prototype) and the analysis plugins.

In recastbackend/backendtasks.py a [Celery](http://www.celeryproject.org/) shared_task provides a wrapper function around a user-specified python function entry point. This wrapper will execute setup and teardown actions before executing the entry point.

Currently a catalogue of existing plugins is hardcoded into recastbackend/catalogue.py, but it is foreseen to have this configurable.

Any analysis plugin VM must have this package insstalled in addition to the plugin code. Once the environment is prepared for analysis, one can start a Celery worker process via 

    celery worker -A recastbackend.fromenvapp:app -l info -Q <queue name>
  
to start accepting RECAST analysis jobs.


#### Docker Compose example for CAP plugin:

when connected to a docker daemon via DOCKER_HOST (like on a Mac with boot2docker)

    export RECAST_CAP_IN_DOCKER_WORKDIR_VOL=$(docker volume inspect workdirsdata|grep Mountpoint|awk '{print $NF}'|sed 's|\"||g')
    docker volume create --name workdirsdata                                                                       
    docker-compose -f cap-compose.yml up -d && docker attach misc_headnode_1                                                     

In the head node you can the issue

    recast-directsub cap http://physics.nyu.edu/~lh1132/dummycomplex.zip complex_analysis/fullworkflow.yml /recastdata/outhere --track

this will have the results appear in `/recastdata/outhere`:

    ls -lrt /recastdata/outhere
