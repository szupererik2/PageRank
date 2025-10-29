import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.joinpath('src')))

import src.Parser as par
import src.PageRank as pagerank
from pathlib import Path
import os
from datetime import datetime

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

    # Also write the ranking (only the function ranking) to a text file in the repo root.
    # Keep terminal output unchanged; the file will contain the same lines that were printed above.
    out_file = Path(__file__).resolve().parent.joinpath('pageranks.txt')
    try:
        with out_file.open('w', encoding='utf-8') as fh:
            for name, score in items:
                fh.write(f"{score:.6f}\t{name}\n")
        print(f"Wrote PageRank results to {out_file}")
    except Exception:
        traceback.print_exc()

    TOP_N = 50
    top = [name for name, _ in items[:TOP_N]]

    sub = src.Graph.Graph() if False else None
    from src.Graph import Graph as _G
    sub = _G()
    for n in top:
        sub.add_node(n)
    for src_node, dests in g.adj_list.items():
        if src_node not in sub.adj_list:
            continue
        for d in dests:
            if d in sub.adj_list:
                sub.add_edge(src_node, d)

    if items:
        scores = [ranks[n] for n in top]
        mn = min(scores)
        mx = max(scores)
        span = mx - mn if mx > mn else 1.0
        node_attrs = {}
        for n in top:
            s = ranks.get(n, 0.0)
            v = (s - mn) / span
            gray = int(255 - v * 150)
            fill = f"#{gray:02x}{gray:02x}{gray:02x}"
            short = n.split(':',1)[1] if ':' in n else n
            node_attrs[n] = {"label": f"{short}\n{ranks.get(n,0):.4f}", "style": "filled", "fillcolor": fill}

    out_dir = Path('img')
    out_dir.mkdir(parents=True, exist_ok=True)
    # use timestamped filename to avoid clobbering and make outputs unique
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_path = str(out_dir.joinpath(f'top50_{ts}'))
    try:
        rendered = sub.visualise(nodes=top, node_attrs=node_attrs, filename=out_path, view=False, format='png')
        print('Rendered top graph to', rendered)
    except Exception:
        traceback.print_exc()