from unittest.mock import MagicMock

from kubernetes.client.exceptions import ApiException


def _make_pod(name: str, namespace: str = "default") -> MagicMock:
    pod = MagicMock()
    pod.metadata.name = name
    pod.metadata.namespace = namespace
    pod.metadata.labels = {"app": name}
    pod.status.phase = "Running"
    pod.status.pod_ip = "10.0.0.1"
    pod.status.container_statuses = []
    pod.spec.node_name = "node-1"
    container = MagicMock()
    container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
    container.resources.limits = {"cpu": "200m", "memory": "256Mi"}
    pod.spec.containers = [container]
    return pod


def test_pods_list(client, mock_k8s):
    mock_k8s.get_pods_in_namespace.return_value = [_make_pod("my-pod")]
    mock_k8s.get_pod_metrics.return_value = {}

    resp = client.get("/api/1/namespaces/default/pods")

    assert resp.status_code == 200
    pods = resp.json()
    assert len(pods) == 1
    pod = pods[0]
    assert pod["name"] == "my-pod"
    assert pod["namespace"] == "default"
    assert pod["status"] == "Running"
    assert pod["ip"] == "10.0.0.1"
    assert pod["node"] == "node-1"
    assert pod["cpu"]["requested"] == 100
    assert pod["memory"]["limit"] == 256 * 1024**2


def test_pods_list_with_metrics(client, mock_k8s):
    mock_k8s.get_pods_in_namespace.return_value = [_make_pod("my-pod")]
    mock_k8s.get_pod_metrics.return_value = {
        ("default", "my-pod"): {"cpu": 42, "memory": 50 * 1024**2}
    }

    resp = client.get("/api/1/namespaces/default/pods")

    pod = resp.json()[0]
    assert pod["cpu"]["used"] == 42
    assert pod["memory"]["used"] == 50 * 1024**2


def test_pod_detail(client, mock_k8s):
    mock_k8s.get_pod.return_value = _make_pod("my-pod")
    mock_k8s.get_pod_metrics.return_value = {}
    mock_k8s.get_services_for_pod.return_value = []
    mock_k8s.get_ingresses_for_services.return_value = []
    mock_k8s.get_pod_events.return_value = []
    mock_k8s.get_pod_logs.return_value = "log line 1\n"

    resp = client.get("/api/1/namespaces/default/pods/my-pod")

    assert resp.status_code == 200
    detail = resp.json()
    assert detail["name"] == "my-pod"
    assert detail["logs"] == "log line 1\n"
    assert detail["services"] == []
    assert detail["ingresses"] == []
    assert detail["events"] == []


def test_pod_not_found(client, mock_k8s):
    mock_k8s.get_pod.side_effect = ApiException(status=404)

    resp = client.get("/api/1/namespaces/default/pods/missing-pod")

    assert resp.status_code == 404
    assert "missing-pod" in resp.json()["detail"]


def test_pod_detail_with_service(client, mock_k8s):
    svc = MagicMock()
    svc.metadata.name = "my-svc"
    svc.spec.type = "ClusterIP"
    svc.spec.cluster_ip = "10.96.0.1"
    port = MagicMock()
    port.port = 80
    port.protocol = "TCP"
    svc.spec.ports = [port]

    mock_k8s.get_pod.return_value = _make_pod("my-pod")
    mock_k8s.get_pod_metrics.return_value = {}
    mock_k8s.get_services_for_pod.return_value = [svc]
    mock_k8s.get_ingresses_for_services.return_value = []
    mock_k8s.get_pod_events.return_value = []
    mock_k8s.get_pod_logs.return_value = ""

    resp = client.get("/api/1/namespaces/default/pods/my-pod")

    assert resp.status_code == 200
    detail = resp.json()
    assert len(detail["services"]) == 1
    assert detail["services"][0]["name"] == "my-svc"
    assert detail["services"][0]["ports"] == ["80/TCP"]
