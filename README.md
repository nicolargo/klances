Klances is the Glances of Kubernetes.

## What is Klances ?

It's a *read-only* WebUI dashboard for Kubernetes cluster monitoring. It's aims to be an user-friendly for monitoring Kubernetes cluster for end-user not familiar with Kubernetes, and also a useful tool for Kubernetes cluster administrators or developers that want to have a quick glance of the cluster status.

It's also provided a fully functional REST API for integration with other tools or for custom monitoring solutions.

## Technology Stack

Backend: Python, FastAPI, Kubernetes Python Client
Frontend: Vue.js

## Features

Top menu with cluster name, cluster status, and refresh button
Node list with CPU, Memory
Namespace list with CPU, Memory and Pod count
Pod list with CPU, Memory and status
Pod details with services/ingress, events and logs
