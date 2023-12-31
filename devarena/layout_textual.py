#!/usr/bin/env python
# -*- coding: utf-8 -*-

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.events import Mount
from textual.containers import Container
from textual.widgets import Header, Footer, Log, DataTable, SelectionList
from textual.widgets.selection_list import Selection

import kubernetes as k8s

import logging

# Create a logger instance for this module and make it log in /tmp/test.log file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/tmp/test.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


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

    @on(Mount)
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

    @on(Mount)
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

    @on(SelectionList.SelectedChanged)
    def update_pods(self):
        # Get the current selected namespaces
        selected_namespaces = self.query_one('#namespaces', SelectionList).selected
        pods = self.k8s_pods(namespaces=selected_namespaces)

        # Update the pods table
        pods_plugin = self.query_one('#pods', DataTable)
        pods_plugin.border_title = "{} in namespaces {}".format(
            '{} pods'.format(len(pods) - 1) if len(pods) > 1 else 'No pod',
            ', '.join(selected_namespaces) if selected_namespaces != [] else '')
        pods_plugin.clear()
        # Update column the first time
        # pods_plugin.columns.clear() may be better ?
        if len(pods_plugin.columns) == 0:
            pods_plugin.add_columns(*pods[0])
        pods_plugin.add_rows(pods[1:])

    # LOGS

    def k8s_logs(self, namespaces=[]) -> list:
        logs = []
        for i in self.v1.list_pod_for_all_namespaces(watch=False).items:
            if i.metadata.namespace in namespaces or namespaces == []:
                logs.append(self.v1.read_namespaced_pod_log(name=i.metadata.name,
                                                            namespace=i.metadata.namespace))
        return logs

    @on(SelectionList.SelectedChanged)
    def update_logs(self):
        # Get the current selected namespaces
        selected_namespaces = self.query_one('#namespaces', SelectionList).selected

        logs_plugin = self.query_one('#logs', Log)
        logs_plugin.border_title = "Logs in namespaces {}".format(
            ', '.join(selected_namespaces) if selected_namespaces != [] else '')
        logs_plugin.clear()
        logs_plugin.write_lines(self.k8s_logs(namespaces=selected_namespaces),
                                scroll_end=None)

    # LAYOUT (update)

    def on_mount(self) -> None:
        pass

    def on_ready(self) -> None:
        self.update_pods()
        self.update_logs()

    # LAYOUT (create)

    def compose(self) -> ComposeResult:
        # yield Header()

        # # https://textual.textualize.io/widgets/data_table/#datatable
        # yield DataTable(classes="box", id="nodes")

        # # https://textual.textualize.io/widgets/selection_list/#selectionlist
        # namespaces = self.k8s_namespaces()
        # namespaces_list = [Selection(*i) for i in namespaces]
        # yield SelectionList[str](
        #     *namespaces_list,
        #     classes="box",
        #     id="namespaces"
        # )

        # # https://textual.textualize.io/widgets/data_table/#datatable
        # yield DataTable(classes="box", id="pods")

        # # https://textual.textualize.io/widgets/log/#log
        # yield Log(classes="box", id="logs",
        #           highlight=True, auto_scroll=True)

        # yield Footer()

        yield Header()
        namespaces = self.k8s_namespaces()
        namespaces_list = [Selection(*i) for i in namespaces]
        yield Container(DataTable(classes="box", id="nodes"),
                        Container(
                            SelectionList[str](
                                *namespaces_list,
                                classes="box",
                                id="namespaces"
                            ),
                            DataTable(classes="box", id="pods"),
                            id="middle"),
                        Log(classes="box", id="logs", highlight=True, auto_scroll=True),
                        id="main")
        yield Footer()


if __name__ == "__main__":
    app = KlanceLayout()
    app.run()
