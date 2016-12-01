## Example Docker Compose setups to set up a RECAST cluster

1. prepare storage and secrets

   this will prepare data volumes and containers holding secrets and set environment variables that will be used in docker compose

   ```
   source setupdockerlocal.sh
   ```

2. start docker compose

   this wills start a the containers related to the recast.

   * a head node with recast-backend (this allows to submit recast requests)
   * a messaging layer (redis, used both for logging and by recast-celery as a job broker)
   * a recast plugin (here: a yadage-enabled pluging running parallel docker containers)

   ```
   docker-compose -f cap-compose-local.yml up -d
   ```
