#!/bin/bash

docker build -t roller-bot .
docker run -d --name roller-bot roller-bot