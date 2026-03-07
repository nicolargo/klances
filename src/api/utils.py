def parse_cpu(cpu_str: str | None) -> int | None:
    """Convert a Kubernetes CPU string to millicores (int)."""
    if not cpu_str:
        return None
    if cpu_str.endswith("m"):
        return int(cpu_str[:-1])
    if cpu_str.endswith("n"):
        return int(cpu_str[:-1]) // 1_000_000
    try:
        return int(float(cpu_str) * 1000)
    except ValueError:
        return None


def parse_memory(mem_str: str | None) -> int | None:
    """Convert a Kubernetes memory string to bytes (int)."""
    if not mem_str:
        return None
    suffixes = {
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Ti": 1024**4,
        "Pi": 1024**5,
        "Ei": 1024**6,
        "k": 1000,
        "M": 1000**2,
        "G": 1000**3,
        "T": 1000**4,
        "P": 1000**5,
        "E": 1000**6,
    }
    for suffix, multiplier in suffixes.items():
        if mem_str.endswith(suffix):
            try:
                return int(float(mem_str[: -len(suffix)]) * multiplier)
            except ValueError:
                return None
    try:
        return int(mem_str)
    except ValueError:
        return None


def get_node_roles(node) -> list[str]:
    """Extract roles from node labels (e.g. node-role.kubernetes.io/control-plane)."""
    labels = node.metadata.labels or {}
    roles = [
        key.split("/")[1]
        for key in labels
        if key.startswith("node-role.kubernetes.io/")
    ]
    return roles or ["worker"]


def get_node_status(node) -> str:
    """Return 'Ready', 'NotReady', or 'Unknown' from node conditions."""
    for cond in node.status.conditions or []:
        if cond.type == "Ready":
            return "Ready" if cond.status == "True" else "NotReady"
    return "Unknown"


def get_pod_status(pod) -> str:
    """Return a human-readable pod status string."""
    phase = pod.status.phase or "Unknown"
    if phase == "Running":
        for cs in pod.status.container_statuses or []:
            if cs.state and cs.state.waiting:
                return cs.state.waiting.reason or "Pending"
    return phase


def aggregate_pod_resources(
    pod,
) -> tuple[int | None, int | None, int | None, int | None]:
    """Return (cpu_requested, cpu_limit, mem_requested, mem_limit) summed across all containers."""
    cpu_req = cpu_lim = mem_req = mem_lim = 0
    has_req = has_lim = False
    for container in pod.spec.containers or []:
        res = container.resources
        if not res:
            continue
        if res.requests:
            cpu_req += parse_cpu(res.requests.get("cpu")) or 0
            mem_req += parse_memory(res.requests.get("memory")) or 0
            has_req = True
        if res.limits:
            cpu_lim += parse_cpu(res.limits.get("cpu")) or 0
            mem_lim += parse_memory(res.limits.get("memory")) or 0
            has_lim = True
    return (
        cpu_req if has_req else None,
        cpu_lim if has_lim else None,
        mem_req if has_req else None,
        mem_lim if has_lim else None,
    )
