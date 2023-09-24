# -*- coding: utf-8 -*-
#
# This file is part of Klances.
#
# SPDX-FileCopyrightText: 2023 Nicolas Hennion <nicolas@nicolargo.com>
#
# SPDX-License-Identifier: MIT
#

import kubernetes as k8s

# Configs can be set in Configuration class directly or using helper utility
k8s.config.load_kube_config()
v1 = k8s.client.CoreV1Api()

# List all nodes
ret = v1.list_node()
for i in ret.items:
    print("\t".join([i.status.addresses[0].address,
                     i.metadata.name,
                     i.status.capacity['cpu'],
                     i.status.capacity['memory']]))

# List all namespaces
ret = v1.list_namespace()
print([n.metadata.name for n in ret.items])

# List all pods
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# List pods in a specific namespace
ret = v1.list_namespaced_pod(namespace="default")
print(ret)

# Simulate get pod logs
ret = v1.read_namespaced_pod_log(name="etcd-minikube", namespace="kube-system")
print(ret)

# Watch events for all pods
count = 5
w = k8s.watch.Watch()
for event in w.stream(v1.list_pod_for_all_namespaces, _request_timeout=60):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    count -= 1
    if not count:
        w.stop()
