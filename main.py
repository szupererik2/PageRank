import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.joinpath('src')))

import src.Parser as par
import src.PageRank as pagerank

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    try:
        g = par.build_graph(path)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
    try:
        ranks = pagerank.RankPage(g)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
    items = sorted(ranks.items(), key=lambda kv: kv[1], reverse=True)
    for name, score in items:
        print(f"{score:.6f}\t{name}")