#!/bin/bash

(cd ../app && docker-compose down)

(cd playback && docker-compose down)

(cd databus && docker-compose down)

docker network rm proxy-redirect
