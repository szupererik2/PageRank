import os


class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_node(self, node_name):
        self.adj_list.setdefault(node_name, [])

    def add_edge(self, src, dest):
        if src not in self.adj_list:
            self.add_node(src)
        if dest not in self.adj_list:
            self.add_node(dest)
        self.adj_list[src].append(dest)

    def visualise(self):
        try:
            from graphviz import Digraph
        except ImportError as e:
            raise ImportError("The 'graphviz' package is required to use visualise(). Install it with pip.") from e
        
        dot = Digraph(comment='Graph')
        for node in self.adj_list:
            dot.node(str(node))

        for src, dests in self.adj_list.items():
            for dest in dests:
                dot.edge(str(src), str(dest))

        output_path = dot.render(filename='graph', format='png', view=True, cleanup=True)
        return output_path

