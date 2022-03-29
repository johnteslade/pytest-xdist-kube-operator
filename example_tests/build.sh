#!/bin/bash

docker build -t johnteslade/pytest-xdist-k8s:example-tests .
docker push johnteslade/pytest-xdist-k8s:example-tests
