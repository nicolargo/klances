from unittest.mock import MagicMock


def _make_node(name: str, ready: bool = True, role: str = "control-plane") -> MagicMock:
    node = MagicMock()
    node.metadata.name = name
    node.metadata.labels = {f"node-role.kubernetes.io/{role}": ""}
    cond = MagicMock()
    cond.type = "Ready"
    cond.status = "True" if ready else "False"
    node.status.conditions = [cond]
    node.status.node_info.kubelet_version = "v1.28.0"
    node.status.capacity = {"cpu": "4", "memory": "8Gi"}
    node.status.allocatable = {"cpu": "3900m", "memory": "7Gi"}
    return node


def test_nodes_list_with_metrics(client, mock_k8s):
    mock_k8s.get_nodes.return_value = [_make_node("node-1")]
    mock_k8s.get_node_metrics.return_value = {
        "node-1": {"cpu": 1200, "memory": 3 * 1024**3}
    }

    resp = client.get("/api/1/nodes")

    assert resp.status_code == 200
    nodes = resp.json()
    assert len(nodes) == 1
    node = nodes[0]
    assert node["name"] == "node-1"
    assert node["roles"] == ["control-plane"]
    assert node["status"] == "Ready"
    assert node["cpu"]["capacity"] == 4000
    assert node["cpu"]["allocatable"] == 3900
    assert node["cpu"]["used"] == 1200
    assert node["memory"]["capacity"] == 8 * 1024**3
    assert node["memory"]["used"] == 3 * 1024**3


def test_nodes_no_metrics(client, mock_k8s):
    mock_k8s.get_nodes.return_value = [_make_node("node-1")]
    mock_k8s.get_node_metrics.return_value = {}

    resp = client.get("/api/1/nodes")

    assert resp.status_code == 200
    node = resp.json()[0]
    assert node["cpu"]["used"] is None
    assert node["memory"]["used"] is None


def test_node_not_ready(client, mock_k8s):
    mock_k8s.get_nodes.return_value = [_make_node("node-1", ready=False, role="worker")]
    mock_k8s.get_node_metrics.return_value = {}

    resp = client.get("/api/1/nodes")

    assert resp.status_code == 200
    node = resp.json()[0]
    assert node["status"] == "NotReady"
    assert node["roles"] == ["worker"]
