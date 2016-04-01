docker volume create --name workdirsdata                                                                       
docker volume create --name quarantine
docker volume create --name secrets
docker run -v secrets:/secrets -it -d --name secrets busybox tail -f /dev/null
docker cp dummyssh/ secrets:/secrets/ssh
docker cp $DOCKER_CERT_PATH secrets:/secrets/certs
export RECAST_IN_DOCKER_WORKDIRS_VOL=$(docker volume inspect workdirsdata|grep Mountpoint|awk '{print $NF}'|sed 's|\"||g')
