import kopf
import kubernetes
import logging

logger = logging.getLogger(__name__)


@kopf.on.create('jtes.net', 'v1', 'pytestxdist')
def create_fn(body, spec, **kwargs):

    # Get info from pytestxdist object
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']

    # Config values
    num_nodes = spec['num_nodes']
    image = spec['image']
    socket_server_port = spec['socket_server_port']
    pytest_dir = spec['pytest_dir']
    extra_pytest_args = spec['extra_pytest_args']

    # Object used to communicate with the API Server
    api = kubernetes.client.CoreV1Api()

    # Create nodes
    for node_num in range(1, num_nodes + 1):

        node_name = f"{name}-node-{node_num}"

        pod_labels = {
            "pytest_run": name,
            "pytest_node": f"{node_num}"
        }

        node_pod = {
            "apiVersion": "v1",
            "metadata": {
                "name": node_name,
                "labels": pod_labels,
            },
            "spec": {
                "containers": [
                    {
                        "image": image,
                        "name": "node",
                        "command": ["python"],
                        "args": [
                            "/socketserver.py",
                            f"0.0.0.0:{socket_server_port}"
                        ],
                        "imagePullPolicy": "Always",
                    }
                ],
                "imagePullSecrets": [{"name": "regcred"}],
                "restartPolicy": "Never",
            },
        }

        # Service template
        svc = {
            "apiVersion": "v1",
            "metadata": {
                "name": node_name
            },
            "spec": {
                "selector": pod_labels,
                "ports": [
                    {
                        "port": socket_server_port,
                        "targetPort": socket_server_port,
                    }
                ],
            },
        }

        # Make the Pod and Service the children of the grafana object
        kopf.adopt(node_pod, owner=body)
        kopf.adopt(svc, owner=body)

        # Create Pod
        obj = api.create_namespaced_pod(namespace, node_pod)
        logger.info(f"Pod {obj.metadata.name} created")

        # Create Service
        obj = api.create_namespaced_service(namespace, svc)
        logger.info(f"Service {obj.metadata.name} created")

    # Create master pod

    # Run in distributed mode and set all the services above as nodes
    pytest_args = ["-d"]
    for node_num in range(1, num_nodes + 1):
        pytest_args += [
            "--tx",
            f"socket={name}-node-{node_num}:{socket_server_port}"
        ]
    # Rsync for the test data
    pytest_args += ["--rsyncdir", pytest_dir, pytest_dir]
    pytest_args += extra_pytest_args

    master_pod = {
        "apiVersion": "v1",
        "metadata": {
            "name": f"{name}-master",
        },
        "spec": {
            "containers": [
                {
                    "image": image,
                    "name": "master",
                    "command": ["pytest"],
                    "args": pytest_args,
                    "imagePullPolicy": "Always",
                }
            ],
            "imagePullSecrets": [{"name": "regcred"}],
            "restartPolicy": "Never",
        },
    }

    # Make the Pod and Service the children of the grafana object
    kopf.adopt(master_pod, owner=body)

    # Create Pod
    obj = api.create_namespaced_pod(namespace, master_pod)
    logger.info(f"Pod {obj.metadata.name} created")

    # Update status
    msg = f"Pods and services created for {name}"
    return {'message': msg}


@kopf.on.delete('jtes.net', 'v1', 'pytestxdist')
def delete(body, **kwargs):
    msg = f"Grafana {body['metadata']['name']} and children deleted"
    return {'message': msg}
