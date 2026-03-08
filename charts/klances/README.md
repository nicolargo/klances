# Klances Helm Chart

A read-only Kubernetes dashboard — the Glances of Kubernetes.

Klances provides a clean, lightweight WebUI and REST API for monitoring your Kubernetes cluster without any write access. It displays nodes, namespaces, pods, services, ingresses, events, and logs in a single-page dashboard.

For more information, see the [main repository](https://github.com/nicolargo/klances).

## Prerequisites

- Kubernetes >= 1.21
- Helm >= 3.8

## Installation

```bash
# Add the Klances Helm repository
helm repo add klances https://nicolargo.github.io/klances
helm repo update

# Install Klances
helm install klances klances/klances
```

To install in a specific namespace:

```bash
helm install klances klances/klances --namespace monitoring --create-namespace
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|---|---|---|
| `replicaCount` | Number of pod replicas | `1` |
| `image.repository` | Container image repository | `klances` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `image.tag` | Image tag (defaults to chart `appVersion`) | `""` |
| `imagePullSecrets` | Docker registry secret names | `[]` |
| `nameOverride` | Override the chart name | `""` |
| `fullnameOverride` | Override the full release name | `""` |
| `serviceAccount.create` | Create a dedicated ServiceAccount | `true` |
| `serviceAccount.annotations` | Annotations for the ServiceAccount | `{}` |
| `serviceAccount.name` | Override the ServiceAccount name | `""` |
| `rbac.create` | Create ClusterRole and ClusterRoleBinding | `true` |
| `service.type` | Kubernetes Service type | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `ingress.enabled` | Enable Ingress resource | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress host rules | `[{host: klances.local, paths: [{path: /, pathType: Prefix}]}]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |
| `resources` | CPU/memory requests and limits | `{}` |
| `nodeSelector` | Node labels for pod assignment | `{}` |
| `tolerations` | Tolerations for pod scheduling | `[]` |
| `affinity` | Affinity rules for pod scheduling | `{}` |

You can override any parameter with `--set` or by providing a custom `values.yaml`:

```bash
helm install klances klances/klances \
  --set service.port=9000 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=128Mi
```

## RBAC & Security

When `rbac.create` is `true` (the default), the chart creates a **ClusterRole** with strictly **read-only** permissions and binds it to the Klances ServiceAccount. Klances never modifies your cluster.

The ClusterRole grants the following access:

| API Group | Resources | Verbs |
|---|---|---|
| `""` (core) | pods, pods/log, nodes, namespaces, services, events | get, list, watch |
| `apps` | deployments | get, list, watch |
| `networking.k8s.io` | ingresses | get, list, watch |
| `metrics.k8s.io` | nodes, pods | get, list |

No write, create, update, patch, or delete permissions are granted. This is the minimum set of permissions required for Klances to function.

If you manage RBAC externally, set `rbac.create=false` and ensure the ServiceAccount has equivalent read-only access.

## Upgrading

```bash
helm repo update
helm upgrade klances klances/klances
```

## Uninstalling

```bash
helm uninstall klances
```

This removes all Kubernetes resources created by the chart (Deployment, Service, ServiceAccount, ClusterRole, ClusterRoleBinding, and Ingress if enabled).

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](https://github.com/nicolargo/klances/blob/main/CONTRIBUTING.md) for guidelines.
