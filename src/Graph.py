import os


class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_node(self, node_name):
        print(f"Node added : {node_name}")
        self.adj_list.setdefault(node_name, [])

    def add_edge(self, src, dest):
        if src not in self.adj_list:
            self.add_node(src)
        if dest not in self.adj_list:
            self.add_node(dest)
        self.adj_list[src].append(dest)
    def get_nodes(self):
        return list(self.adj_list.keys())

    def out_degree(self, node):
        return list(self.adj_list.get(node, []))

    def in_degree(self, node):
        res = []
        for src, dests in self.adj_list.items():
            if node in dests:
                res.append(src)
        return res

    def visualise(self, nodes: list | None = None, node_attrs: dict | None = None, filename: str = 'img/graph', view: bool = False, format: str = 'png'):
        
        try:
            from graphviz import Digraph
        except ImportError as e:
            raise ImportError("The 'graphviz' package is required to use visualise(). Install it with pip.") from e

        if nodes is None:
            include = set(self.get_nodes())
        else:
            include = set(nodes)

        out_dir = os.path.dirname(filename)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        dot = Digraph(comment='Graph')

        id_map = {}
        for i, n in enumerate(sorted(include)):
            nid = f'n{i}'
            id_map[n] = nid
            attrs = {}
            if node_attrs and n in node_attrs:
                attrs.update(node_attrs[n])
            if 'label' not in attrs:
                attrs['label'] = str(n)
            dot.node(nid, **attrs)

        for src, dests in self.adj_list.items():
            if src not in include:
                continue
            for dest in dests:
                if dest not in include:
                    continue
                s = id_map.get(src)
                d = id_map.get(dest)
                if s and d:
                    dot.edge(s, d)

        rendered = dot.render(filename=filename, format=format, view=view, cleanup=True)
        return rendered

