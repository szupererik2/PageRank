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

    def visualise(self, backend: str | None = None):
        try:
            import matplotlib
            if backend:
                matplotlib.use(backend)
            else:
                if os.name == 'posix' and not os.environ.get('DISPLAY'):
                    matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import networkx as nx
        except Exception:
            print("visualise: skipped (networkx/matplotlib not available)")
            return

        G = nx.DiGraph()
        for src, dests in self.adj_list.items():
            for dest in dests:
                G.add_edge(src, dest)

        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=2000,
                arrowstyle="->", arrowsize=20, font_size=12, font_weight="bold")
        plt.show()
        plt.close()
