from pydantic import BaseModel


class ResourceUsage(BaseModel):
    capacity: int | None = None      # nodes: raw capacity
    allocatable: int | None = None   # nodes: schedulable capacity
    requested: int | None = None     # pods/namespaces: sum of requests
    limit: int | None = None         # pods/namespaces: sum of limits
    used: int | None = None          # all: live usage from metrics-server (None if unavailable)


class ClusterInfo(BaseModel):
    name: str
    version: str
    status: str   # "healthy" | "degraded" | "unknown"
    node_count: int


class NodeInfo(BaseModel):
    name: str
    roles: list[str]
    version: str
    status: str   # "Ready" | "NotReady" | "Unknown"
    cpu: ResourceUsage
    memory: ResourceUsage


class NamespaceInfo(BaseModel):
    name: str
    status: str
    pod_count: int
    cpu: ResourceUsage
    memory: ResourceUsage


class PodInfo(BaseModel):
    name: str
    namespace: str
    status: str
    ip: str | None
    node: str | None
    cpu: ResourceUsage
    memory: ResourceUsage


class ServiceInfo(BaseModel):
    name: str
    type: str
    cluster_ip: str | None
    ports: list[str]


class IngressInfo(BaseModel):
    name: str
    host: str | None
    paths: list[str]


class EventInfo(BaseModel):
    type: str | None
    reason: str | None
    message: str | None
    timestamp: str | None


class PodDetail(PodInfo):
    services: list[ServiceInfo]
    ingresses: list[IngressInfo]
    events: list[EventInfo]
    logs: str
