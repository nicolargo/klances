from unittest.mock import MagicMock


def _make_node(ready: bool = True) -> MagicMock:
    node = MagicMock()
    cond = MagicMock()
    cond.type = "Ready"
    cond.status = "True" if ready else "False"
    node.status.conditions = [cond]
    return node


def test_cluster_healthy(client, mock_k8s):
    mock_k8s.get_nodes.return_value = [_make_node(True), _make_node(True)]
    mock_k8s.get_cluster_name.return_value = "test-cluster"
    mock_k8s.get_server_version.return_value = "v1.28.0"

    resp = client.get("/api/1/cluster")

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "test-cluster"
    assert data["version"] == "v1.28.0"
    assert data["status"] == "healthy"
    assert data["node_count"] == 2


def test_cluster_degraded(client, mock_k8s):
    mock_k8s.get_nodes.return_value = [_make_node(True), _make_node(False)]
    mock_k8s.get_cluster_name.return_value = "test-cluster"
    mock_k8s.get_server_version.return_value = "v1.28.0"

    resp = client.get("/api/1/cluster")

    assert resp.status_code == 200
    assert resp.json()["status"] == "degraded"


def test_cluster_empty(client, mock_k8s):
    mock_k8s.get_nodes.return_value = []
    mock_k8s.get_cluster_name.return_value = "empty-cluster"
    mock_k8s.get_server_version.return_value = "v1.28.0"

    resp = client.get("/api/1/cluster")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "unknown"
    assert data["node_count"] == 0
