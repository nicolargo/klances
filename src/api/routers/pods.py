from fastapi import APIRouter, Depends, HTTPException
from kubernetes.client.exceptions import ApiException

from ..k8s_client import K8sClient, get_k8s_client
from ..models import EventInfo, IngressInfo, PodDetail, PodInfo, ResourceUsage, ServiceInfo
from ..utils import aggregate_pod_resources, get_pod_status

router = APIRouter()


def _build_pod_base(pod, metrics: dict) -> dict:
    cpu_req, cpu_lim, mem_req, mem_lim = aggregate_pod_resources(pod)
    return dict(
        name=pod.metadata.name,
        namespace=pod.metadata.namespace,
        status=get_pod_status(pod),
        ip=pod.status.pod_ip,
        node=pod.spec.node_name,
        cpu=ResourceUsage(
            requested=cpu_req,
            limit=cpu_lim,
            used=metrics.get("cpu"),
        ),
        memory=ResourceUsage(
            requested=mem_req,
            limit=mem_lim,
            used=metrics.get("memory"),
        ),
    )


def _build_service_info(svc) -> ServiceInfo:
    ports = [f"{p.port}/{p.protocol}" for p in (svc.spec.ports or [])]
    return ServiceInfo(
        name=svc.metadata.name,
        type=svc.spec.type or "ClusterIP",
        cluster_ip=svc.spec.cluster_ip,
        ports=ports,
    )


def _build_ingress_info(ing) -> IngressInfo:
    paths = []
    for rule in ing.spec.rules or []:
        host = rule.host or "*"
        for path in (rule.http.paths if rule.http else []):
            paths.append(f"{host}{path.path or '/'}")
    return IngressInfo(
        name=ing.metadata.name,
        host=(ing.spec.rules[0].host if ing.spec.rules else None),
        paths=paths,
    )


def _build_event_info(evt) -> EventInfo:
    timestamp = None
    if evt.last_timestamp:
        timestamp = evt.last_timestamp.isoformat()
    elif evt.event_time:
        timestamp = evt.event_time.isoformat()
    return EventInfo(
        type=evt.type,
        reason=evt.reason,
        message=evt.message,
        timestamp=timestamp,
    )


@router.get("/namespaces/{namespace}/pods", response_model=list[PodInfo])
def get_pods(namespace: str, k8s: K8sClient = Depends(get_k8s_client)):
    pods = k8s.get_pods_in_namespace(namespace)
    pod_metrics = k8s.get_pod_metrics(namespace)

    return [
        PodInfo(**_build_pod_base(pod, pod_metrics.get((namespace, pod.metadata.name), {})))
        for pod in pods
    ]


@router.get("/namespaces/{namespace}/pods/{pod_name}", response_model=PodDetail)
def get_pod_detail(namespace: str, pod_name: str, k8s: K8sClient = Depends(get_k8s_client)):
    try:
        pod = k8s.get_pod(namespace, pod_name)
    except ApiException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Pod '{pod_name}' not found in namespace '{namespace}'",
            )
        raise HTTPException(status_code=500, detail=str(e))

    pod_labels = pod.metadata.labels or {}
    pod_metrics = k8s.get_pod_metrics(namespace)
    metrics = pod_metrics.get((namespace, pod_name), {})

    services = k8s.get_services_for_pod(namespace, pod_labels)
    service_names = {svc.metadata.name for svc in services}
    ingresses = k8s.get_ingresses_for_services(namespace, service_names)
    events = k8s.get_pod_events(namespace, pod_name)
    logs = k8s.get_pod_logs(namespace, pod_name)

    return PodDetail(
        **_build_pod_base(pod, metrics),
        services=[_build_service_info(s) for s in services],
        ingresses=[_build_ingress_info(i) for i in ingresses],
        events=[_build_event_info(e) for e in events],
        logs=logs,
    )
