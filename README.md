# pytest-xdist-kube-operator

This is an example Kubernetes operator in Python (using kopf). It allows you
to run pytest in a distributed mode. A number of pods will be started to run
the actual tests and results collected by the master.

## Pytest Example

This is how to run distributed pytest locally. This will be replicated inside
kube.

Run socket servers

    python socketserver.py 0.0.0.0:8888

    python socketserver.py 0.0.0.0:8889


Run test

    pytest -d --tx socket=0.0.0.0:8888 --tx socket=0.0.0.0:8889 --rsyncdir tests tests -v


## CRD setup

build docker image for the operator

    cd pytest-xdist-k8s
    ./build.sh

setup docker perms (be careful of what creds in your local config).

    kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=$(realpath ~/.docker/config.json) \
    --type=kubernetes.io/dockerconfigjson

setup crds

    cd setup
    kubectl apply -f crd.yml
    kubectl apply -f service_account.yml
    kubectl apply -f role.yml
    kubectl apply -f rolebinding.yml
    kubectl apply -f deployment.yml

build the docker image for the tests to be run

    cd example_tests
    ./build.sh

create a custom object

    kubectl delete pytestxdist.jtes.net test1
    kubectl apply -f example-pytestxdist.yml
