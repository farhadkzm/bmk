#!/usr/bin/env bash


docker tag $(docker build -q -t bmk-app .) farhadkzm/bmk-app:latest
docker login
docker push farhadkzm/bmk-app
