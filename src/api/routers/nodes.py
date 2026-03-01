from fastapi import APIRouter, Depends

from ..k8s_client import K8sClient, get_k8s_client
from ..models import NodeInfo, ResourceUsage
from ..utils import get_node_roles, get_node_status, parse_cpu, parse_memory

router = APIRouter()


@router.get("/nodes", response_model=list[NodeInfo])
def get_nodes(k8s: K8sClient = Depends(get_k8s_client)):
    nodes = k8s.get_nodes()
    node_metrics = k8s.get_node_metrics()

    result = []
    for node in nodes:
        name = node.metadata.name
        capacity = node.status.capacity or {}
        allocatable = node.status.allocatable or {}
        metrics = node_metrics.get(name, {})

        result.append(NodeInfo(
            name=name,
            roles=get_node_roles(node),
            version=node.status.node_info.kubelet_version,
            status=get_node_status(node),
            cpu=ResourceUsage(
                capacity=parse_cpu(capacity.get("cpu")),
                allocatable=parse_cpu(allocatable.get("cpu")),
                used=metrics.get("cpu"),
            ),
            memory=ResourceUsage(
                capacity=parse_memory(capacity.get("memory")),
                allocatable=parse_memory(allocatable.get("memory")),
                used=metrics.get("memory"),
            ),
        ))

    return result
