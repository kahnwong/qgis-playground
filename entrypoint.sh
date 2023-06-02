#!/bin/bash

# pull data
cd /opt/data
dvc pull
mv data/* /etc/qgisserver/

# entrypoint: https://github.com/camptocamp/docker-qgis-server/blob/master/Dockerfile#L233
/usr/local/bin/start-server
