from fastapi import APIRouter, Depends

from ..k8s_client import K8sClient, get_k8s_client
from ..models import NamespaceInfo, ResourceUsage
from ..utils import aggregate_pod_resources

router = APIRouter()


@router.get("/namespaces", response_model=list[NamespaceInfo])
def get_namespaces(k8s: K8sClient = Depends(get_k8s_client)):
    namespaces = k8s.get_namespaces()
    all_pods = k8s.get_all_pods()
    pod_metrics = k8s.get_pod_metrics()

    result = []
    for ns in namespaces:
        ns_name = ns.metadata.name
        ns_pods = [p for p in all_pods if p.metadata.namespace == ns_name]

        cpu_req = cpu_lim = mem_req = mem_lim = 0
        cpu_used = mem_used = 0
        has_metrics = False

        for pod in ns_pods:
            pr, pl, mr, ml = aggregate_pod_resources(pod)
            cpu_req += pr or 0
            cpu_lim += pl or 0
            mem_req += mr or 0
            mem_lim += ml or 0

            m = pod_metrics.get((ns_name, pod.metadata.name))
            if m:
                cpu_used += m.get("cpu") or 0
                mem_used += m.get("memory") or 0
                has_metrics = True

        result.append(
            NamespaceInfo(
                name=ns_name,
                status=ns.status.phase or "Unknown",
                pod_count=len(ns_pods),
                cpu=ResourceUsage(
                    requested=cpu_req,
                    limit=cpu_lim,
                    used=cpu_used if has_metrics else None,
                ),
                memory=ResourceUsage(
                    requested=mem_req,
                    limit=mem_lim,
                    used=mem_used if has_metrics else None,
                ),
            )
        )

    return result
