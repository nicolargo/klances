from fastapi import APIRouter, Depends

from ..k8s_client import K8sClient, get_k8s_client
from ..models import ClusterInfo

router = APIRouter()


@router.get("/cluster", response_model=ClusterInfo)
def get_cluster(k8s: K8sClient = Depends(get_k8s_client)):
    nodes = k8s.get_nodes()
    healthy = sum(
        1
        for node in nodes
        for cond in (node.status.conditions or [])
        if cond.type == "Ready" and cond.status == "True"
    )
    if len(nodes) == 0:
        status = "unknown"
    elif healthy == len(nodes):
        status = "healthy"
    else:
        status = "degraded"

    return ClusterInfo(
        name=k8s.get_cluster_name(),
        version=k8s.get_server_version(),
        status=status,
        node_count=len(nodes),
    )
