import logging
from functools import lru_cache

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from .utils import parse_cpu, parse_memory

logger = logging.getLogger(__name__)


class K8sClient:
    def __init__(self) -> None:
        try:
            config.load_incluster_config()
            logger.info("Using in-cluster Kubernetes config")
        except config.ConfigException:
            config.load_kube_config()
            logger.info("Using kubeconfig file")

        self.core = client.CoreV1Api()
        self.version_api = client.VersionApi()
        self.networking = client.NetworkingV1Api()
        self.custom = client.CustomObjectsApi()

    def get_cluster_name(self) -> str:
        try:
            _, ctx = config.list_kube_config_contexts()
            return ctx["context"].get("cluster", "unknown")
        except Exception:
            return "in-cluster"

    def get_server_version(self) -> str:
        try:
            return self.version_api.get_code().git_version
        except ApiException:
            return "unknown"

    def get_nodes(self) -> list:
        return self.core.list_node().items

    def get_namespaces(self) -> list:
        return self.core.list_namespace().items

    def get_all_pods(self) -> list:
        return self.core.list_pod_for_all_namespaces().items

    def get_pods_in_namespace(self, namespace: str) -> list:
        return self.core.list_namespaced_pod(namespace=namespace).items

    def get_pod(self, namespace: str, pod_name: str):
        return self.core.read_namespaced_pod(name=pod_name, namespace=namespace)

    def get_node_metrics(self) -> dict[str, dict]:
        """Return node metrics keyed by node name. Empty dict if metrics-server is unavailable."""
        try:
            result = self.custom.list_cluster_custom_object(
                group="metrics.k8s.io", version="v1beta1", plural="nodes"
            )
            return {
                item["metadata"]["name"]: {
                    "cpu": parse_cpu(item.get("usage", {}).get("cpu")),
                    "memory": parse_memory(item.get("usage", {}).get("memory")),
                }
                for item in result.get("items", [])
            }
        except ApiException:
            logger.warning("Node metrics API unavailable (metrics-server not installed?)")
            return {}

    def get_pod_metrics(self, namespace: str | None = None) -> dict[tuple[str, str], dict]:
        """Return pod metrics keyed by (namespace, pod_name). Empty dict if metrics-server is unavailable."""
        try:
            if namespace:
                result = self.custom.list_namespaced_custom_object(
                    group="metrics.k8s.io", version="v1beta1",
                    namespace=namespace, plural="pods",
                )
            else:
                result = self.custom.list_cluster_custom_object(
                    group="metrics.k8s.io", version="v1beta1", plural="pods"
                )
            metrics: dict[tuple[str, str], dict] = {}
            for item in result.get("items", []):
                ns = item["metadata"]["namespace"]
                name = item["metadata"]["name"]
                cpu = sum(
                    parse_cpu(c["usage"]["cpu"]) or 0
                    for c in item.get("containers", [])
                    if c.get("usage", {}).get("cpu")
                )
                memory = sum(
                    parse_memory(c["usage"]["memory"]) or 0
                    for c in item.get("containers", [])
                    if c.get("usage", {}).get("memory")
                )
                metrics[(ns, name)] = {"cpu": cpu, "memory": memory}
            return metrics
        except ApiException:
            logger.warning("Pod metrics API unavailable (metrics-server not installed?)")
            return {}

    def get_services_for_pod(self, namespace: str, pod_labels: dict) -> list:
        """Return services whose selector matches the pod's labels."""
        services = self.core.list_namespaced_service(namespace=namespace).items
        return [
            svc for svc in services
            if svc.spec.selector and all(
                pod_labels.get(k) == v for k, v in svc.spec.selector.items()
            )
        ]

    def get_ingresses_for_services(self, namespace: str, service_names: set[str]) -> list:
        """Return ingresses that route to any of the given services."""
        if not service_names:
            return []
        try:
            ingresses = self.networking.list_namespaced_ingress(namespace=namespace).items
            result = []
            for ing in ingresses:
                for rule in ing.spec.rules or []:
                    if rule.http and any(
                        path.backend.service.name in service_names
                        for path in rule.http.paths or []
                    ):
                        result.append(ing)
                        break
            return result
        except ApiException:
            return []

    def get_pod_events(self, namespace: str, pod_name: str) -> list:
        return self.core.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={pod_name}",
        ).items

    def get_pod_logs(self, namespace: str, pod_name: str, tail_lines: int = 100) -> str:
        try:
            return self.core.read_namespaced_pod_log(
                name=pod_name, namespace=namespace, tail_lines=tail_lines
            ) or ""
        except ApiException:
            return ""


@lru_cache(maxsize=1)
def get_k8s_client() -> K8sClient:
    return K8sClient()
