#!/usr/bin/env python
# -*- coding: utf-8 -*-

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.events import Mount
from textual.widgets import Header, Footer, Log, DataTable, SelectionList
from textual.widgets.selection_list import Selection


import kubernetes as k8s


class KlanceLayout(App):
    CSS_PATH = "layout_textual.tcss"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        # Binding(
        #     key="question_mark",
        #     action="help",
        #     description="Show help screen",
        #     key_display="?",
        # ),
        # Binding(key="j", action="down", description="Scroll down", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.k8s_connect()

    def k8s_connect(self):
        k8s.config.load_kube_config()
        self.v1 = k8s.client.CoreV1Api()

    # NODES

    def k8s_nodes(self) -> list:
        nodes = []
        # Set the column names
        nodes.append(('Name', 'Address', 'CPU', 'Memory'))
        for i in self.v1.list_node().items:
            nodes.append((i.metadata.name,
                          i.status.addresses[0].address,
                          i.status.capacity['cpu'],
                          i.status.capacity['memory']))
        return nodes

    def update_nodes(self):
        nodes_plugin = self.query_one('#nodes', DataTable)
        nodes = self.k8s_nodes()
        nodes_plugin.add_columns(*nodes[0])
        nodes_plugin.add_rows(nodes[1:])

    # NAMESPACES

    def k8s_namespaces(self) -> list:
        namespaces = []
        for i in self.v1.list_namespace().items:
            namespaces.append(("{} ({})".format(i.metadata.name,
                                                i.status.phase),
                               i.metadata.name))
        return namespaces

    def update_namespaces(self):
        self.query_one('#namespaces', SelectionList).border_title = "Select namespaces"

    # PODS

    def k8s_pods(self, namespaces=[]) -> list:
        pods = []
        # Set the column names
        pods.append(('Name', 'Namespace', 'IP'))
        if namespaces == []:
            # Get pods from all namespaces
            for i in self.v1.list_pod_for_all_namespaces(watch=False).items:
                pods.append((i.metadata.name,
                            i.metadata.namespace,
                            i.status.pod_ip))
        else:
            # Get pods from selected namespaces
            for namespace in namespaces:
                for i in self.v1.list_namespaced_pod(namespace=namespace).items:
                    pods.append((i.metadata.name,
                                i.metadata.namespace,
                                i.status.pod_ip))
        return pods

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_pods(self):
        selected_namespaces = self.query_one('#namespaces', SelectionList).selected
        pods_plugin = self.query_one('#pods', DataTable)
        pods_plugin.border_title = "Pods in namespace {}".format(selected_namespaces)
        pods = self.k8s_pods(namespaces=selected_namespaces)
        pods.clear()
        pods_plugin.add_columns(*pods[0])
        pods_plugin.add_rows(pods[1:])

    # LOGS

    def k8s_logs(self) -> list:
        logs = []
        for i in self.v1.list_pod_for_all_namespaces(watch=False).items:
            logs.append(self.v1.read_namespaced_pod_log(name=i.metadata.name,
                                                        namespace=i.metadata.namespace))
        return logs

    def update_logs(self):
        self.query_one(Log).write_lines(self.k8s_logs(),
                                        scroll_end=None)

    # LAYOUT (update)

    def on_mount(self) -> None:
        self.update_nodes()
        self.update_namespaces()
        # Sure ? better to call it from callback namespace ?
        self.update_pods()

    def on_ready(self) -> None:
        self.update_logs()

    # LAYOUT (create)

    def compose(self) -> ComposeResult:
        yield Header()

        # https://textual.textualize.io/widgets/data_table/#datatable
        yield DataTable(classes="box", id="nodes")

        # https://textual.textualize.io/widgets/data_table/#datatable
        namespaces = self.k8s_namespaces()
        namespaces_list = [Selection(*i) for i in namespaces]
        yield SelectionList[str](
            *namespaces_list,
            classes="box",
            id="namespaces"
        )

        # https://textual.textualize.io/widgets/data_table/#datatable
        yield DataTable(classes="box", id="pods")

        # https://textual.textualize.io/widgets/log/#log
        yield Log(highlight=True, auto_scroll=True, id="logs")

        yield Footer()


if __name__ == "__main__":
    app = KlanceLayout()
    app.run()
