#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from rich import print
from rich.columns import Columns
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.live import Live

from keyboard import KBHit
import kubernetes as k8s


# Create the layout
console = Console()
layout = Layout()
nodes_panel = Panel("[red]Nodes list", title="Nodes", subtitle="x nodes in the cluster")
namespaces_panel = Panel("[red]Namespaces list", title="Namespaces", subtitle="x namespaces in the cluster")
pods_panel = Panel("[red]Pods list", title="Pods", subtitle="x pods in the cluster")
logs_panel = Panel("[red]Logs", title="Logs", subtitle="")
layout.split_column(
    Layout(nodes_panel, name="nodes"),
    Layout(name="middle"),
    Layout(logs_panel, name="logs")
)
layout["middle"].split_row(
    Layout(namespaces_panel, name="namespaces"),
    Layout(pods_panel, name="pods")
)


# Main

# Configs can be set in Configuration class directly or using helper utility
k8s.config.load_kube_config()
v1 = k8s.client.CoreV1Api()

kb = KBHit()
with Live(console=console, screen=True, auto_refresh=False) as live:
    while True:

        # Updates nodes list
        nodes = "\n".join([i.metadata.name for i in v1.list_node().items])
        # for i in ret.items:
        #     print("%s\t%s" % (i.status.addresses[0].address, i.metadata.name))
        layout["nodes"].update(Panel(nodes, title="Nodes", subtitle="x nodes in the cluster"))

        # Updates namespaces list
        namespaces = "\n".join([n.metadata.name for n in v1.list_namespace().items])
        layout["namespaces"].update(Panel(namespaces, title="Namespaces", subtitle="x namespaces in the cluster"))

        # Updates pods list
        pods = "\n".join([i.metadata.name for i in v1.list_pod_for_all_namespaces(watch=False).items])
        layout["pods"].update(Panel(pods, title="Pods", subtitle="x pods in the cluster"))

        # Updates logs for all pods in all namespaces
        logs = ""
        for i in v1.list_pod_for_all_namespaces(watch=False).items:
            logs += v1.read_namespaced_pod_log(name=i.metadata.name,
                                               namespace=i.metadata.namespace)
        layout["logs"].update(Panel(logs, title="Logs", subtitle=""))

        live.update(layout, refresh=True)
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27:  # ESC
                break
        time.sleep(1)
kb.set_normal_term()
