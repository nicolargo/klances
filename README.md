Klances is the Glances of Kubernetes.

## What is Klances ?

It's a *read-only* WebUI dashboard for Kubernetes cluster monitoring. It's aims to be an user-friendly for monitoring Kubernetes cluster for end-user not familiar with Kubernetes, and also a useful tool for Kubernetes cluster administrators or developers that want to have a quick glance of the cluster status.

It's also provided a fully functional REST API for integration with other tools or for custom monitoring solutions.

## Technology Stack

Backend: Python, FastAPI, Kubernetes Python Client
Frontend: Vue.js, eCharts, Tailwind CSS

## Features

Top menu with cluster name, cluster status, and refresh button

Horizontal (full size) panel with 2 columns:

- Node list with roles, version, CPU, Memory
- Namespace list with status, CPU, Memory and Pod count

If a namespace is selected, it will show in another horizontal (full size) panel:

- Pod list with status, CPU, Memory (both with current, requested and limit), ip, node

if a pod is selected, it will show in another horizontal (full size) panel:

- Pod details with services/ingress, events and logs

Bottom menu with links to GitHub repository and license information.

Panels are refreshable with the refresh button in the top menu, and also auto-refresh every 5 seconds (delay configurable through the WebUI).

## License

Klances is licensed under the MIT License. See the LICENSE file for more details.
