#!/bin/bash

docker build -t johnteslade/pytest-xdist-k8s:operator .
docker push johnteslade/pytest-xdist-k8s:operator
