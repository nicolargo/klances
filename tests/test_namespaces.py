from unittest.mock import MagicMock


def _make_namespace(name: str, phase: str = "Active") -> MagicMock:
    ns = MagicMock()
    ns.metadata.name = name
    ns.status.phase = phase
    return ns


def _make_pod(
    name: str, namespace: str, cpu_req: str = "100m", mem_req: str = "128Mi"
) -> MagicMock:
    pod = MagicMock()
    pod.metadata.name = name
    pod.metadata.namespace = namespace
    container = MagicMock()
    container.resources.requests = {"cpu": cpu_req, "memory": mem_req}
    container.resources.limits = {"cpu": "200m", "memory": "256Mi"}
    pod.spec.containers = [container]
    return pod


def test_namespaces_aggregates_pod_resources(client, mock_k8s):
    mock_k8s.get_namespaces.return_value = [_make_namespace("default")]
    mock_k8s.get_all_pods.return_value = [_make_pod("pod-1", "default")]
    mock_k8s.get_pod_metrics.return_value = {}

    resp = client.get("/api/1/namespaces")

    assert resp.status_code == 200
    ns = resp.json()[0]
    assert ns["name"] == "default"
    assert ns["status"] == "Active"
    assert ns["pod_count"] == 1
    assert ns["cpu"]["requested"] == 100
    assert ns["cpu"]["limit"] == 200
    assert ns["cpu"]["used"] is None  # no metrics-server
    assert ns["memory"]["requested"] == 128 * 1024**2
    assert ns["memory"]["used"] is None


def test_namespaces_with_metrics(client, mock_k8s):
    mock_k8s.get_namespaces.return_value = [_make_namespace("default")]
    mock_k8s.get_all_pods.return_value = [_make_pod("pod-1", "default")]
    mock_k8s.get_pod_metrics.return_value = {
        ("default", "pod-1"): {"cpu": 50, "memory": 64 * 1024**2}
    }

    resp = client.get("/api/1/namespaces")

    ns = resp.json()[0]
    assert ns["cpu"]["used"] == 50
    assert ns["memory"]["used"] == 64 * 1024**2


def test_namespaces_filters_pods_by_namespace(client, mock_k8s):
    mock_k8s.get_namespaces.return_value = [
        _make_namespace("default"),
        _make_namespace("kube-system"),
    ]
    mock_k8s.get_all_pods.return_value = [
        _make_pod("pod-a", "default"),
        _make_pod("pod-b", "kube-system"),
        _make_pod("pod-c", "kube-system"),
    ]
    mock_k8s.get_pod_metrics.return_value = {}

    resp = client.get("/api/1/namespaces")

    namespaces = {ns["name"]: ns for ns in resp.json()}
    assert namespaces["default"]["pod_count"] == 1
    assert namespaces["kube-system"]["pod_count"] == 2
