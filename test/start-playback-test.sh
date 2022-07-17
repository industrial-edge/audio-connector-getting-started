#!/bin/bash

# ensure clean test environment
sh ./stop-and-cleanup.sh

# if needed, create proxy-redirect (emulates IED)
docker network create proxy-redirect

# run ie-databus
(cd databus && docker-compose up -d)

# start playback
(cd playback && docker-compose build)
(cd playback && docker-compose up -d)

# run audio processor
(cd ../app && docker-compose build)
(cd ../app && docker-compose up)
