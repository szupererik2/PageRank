import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.Graph import Graph

def test_visualise():
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "E")
    g.add_edge("E", "A")

    g.visualise()

if __name__ == "__main__":
    test_visualise()
