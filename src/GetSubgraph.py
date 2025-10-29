from collections import deque
from .Graph import Graph
def get_subgraph(graph, nodes):
    sub = Graph()
    for node in nodes:
        if node in graph.adj_list:
            for dest in graph.adj_list[node]:
                if dest in nodes:
                    sub.add_edge(node, dest)
    return sub

def get_subgraph_from_node(graph, start_node, max_nodes):
    if start_node not in graph.adj_list:
        raise ValueError(f"Start node '{start_node}' not found in graph.")

    visited = set()
    queue = deque([start_node])
    visited.add(start_node)

    while queue and len(visited) < max_nodes:
        current = queue.popleft()
        for neighbor in graph.adj_list.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
            if len(visited) >= max_nodes:
                break

    return get_subgraph(graph, list(visited))
