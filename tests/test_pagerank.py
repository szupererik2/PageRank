import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.Graph import Graph
from src.PageRank import RankPage


def test_two_node_symmetry():
    g = Graph()
    g.add_edge('A', 'B')
    g.add_edge('B', 'A')

    pr = RankPage(g, epsilon=1e-12, max_iter=1000)

    assert abs(pr['A'] - pr['B']) < 1e-9
    assert abs(sum(pr.values()) - 1.0) < 1e-9


def test_dangling_nodes_sum_to_one():
    g = Graph()
    g.add_edge('A', 'B')
    g.add_node('C')

    pr = RankPage(g, epsilon=1e-12, max_iter=1000)

    total = sum(pr.values())
    assert abs(total - 1.0) < 1e-9
