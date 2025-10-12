class NodeNotFoundError(Exception):
    pass

class Graph:
    adj_list = {}

    def __init__(self):
        pass

    def add_node(self, node_name):
        self.adj_list.setdefault(node_name, [])

    def add_edge(self, src, dest):
        if src not in self.adj_list:
            raise NodeNotFoundError(f'Source node {src} does not exist')
        
        if dest not in self.adj_list:
            raise NodeNotFoundError(f'Destination node {dest} does not exist')
        
        self.adj_list[src].append(dest)
