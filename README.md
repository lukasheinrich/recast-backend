# recast-backend
[![Build Status](https://travis-ci.org/recast-hep/recast-backend.svg?branch=master)](https://travis-ci.org/recast-hep/recast-backend)


The modules provided by this package provide the glue between the [RECAST Control Center](https://github.com/recast-hep/recast-control-center-prototype) and the analysis plugins.

In recastbackend/backendtasks.py a [Celery](http://www.celeryproject.org/) shared_task provides a wrapper function around a user-specified python function entry point. This wrapper will execute setup and teardown actions before executing the entry point.

Currently a catalogue of existing plugins is hardcoded into recastbackend/catalogue.py, but it is foreseen to have this configurable.

Any analysis plugin VM must have this package insstalled in addition to the plugin code. Once the environment is prepared for analysis, one can start a Celery worker process via 

    celery worker -A recastbackend.fromenvapp:app -l info -Q <queue name>
  
to start accepting RECAST analysis jobs.
