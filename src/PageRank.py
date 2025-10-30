from typing import Dict

alpha = 0.15

try:
    import numpy as np
except Exception as e:
    raise ImportError("NumPy is required for the optimized PageRank implementation") from e

_HAS_SCIPY = False
try:
    import scipy.sparse as sp
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False


def _build_matrix(g, nodes, use_sparse: bool = True):
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}

    rows = []
    cols = []
    data = []

    outdeg = np.zeros(n, dtype=float)
    for src in nodes:
        j = index[src]
        outs = list(g.out_degree(src))
        outdeg[j] = len(outs)
        if outdeg[j] > 0:
            weight = 1.0 / outdeg[j]
            for dest in outs:
                i = index.get(dest)
                if i is None:
                    continue
                rows.append(i)
                cols.append(j)
                data.append(weight)

    dangling_mask = outdeg == 0

    if use_sparse and _HAS_SCIPY:
        M = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    else:
        M = np.zeros((n, n), dtype=float)
        for r, c, v in zip(rows, cols, data):
            M[r, c] = v

    return M, dangling_mask


def RankPage(g, epsilon: float = 1e-6, max_iter: int = 100, use_sparse: bool = True) -> Dict:
    if not hasattr(g, 'get_nodes') or not callable(getattr(g, 'get_nodes')):
        raise TypeError("RankPage's parameter must be a graph-like object with a get_nodes() method")

    nodes = g.get_nodes()
    if not nodes:
        return {}

    n = len(nodes)
    M, dangling_mask = _build_matrix(g, nodes, use_sparse=use_sparse)

    pr = np.full(n, 1.0 / n, dtype=float)

    teleport = alpha / n

    for _ in range(max_iter):
        prev = pr.copy()

        dangling_sum = prev[dangling_mask].sum() if dangling_mask.any() else 0.0

        if _HAS_SCIPY and use_sparse and isinstance(M, sp.spmatrix):
            mv = M.dot(prev)
        else:
            mv = M @ prev

        pr = (1 - alpha) * (mv + dangling_sum / n) + teleport

        delta = np.abs(pr - prev).sum()
        if delta < epsilon:
            break

    return {node: float(pr[i]) for i, node in enumerate(nodes)}


def RankCalc(g, PR):
    new_PR = {}
    nodes = g.get_nodes()
    n = len(nodes)

    for node in nodes:
        inbound_nodes = g.in_degree(node)
        rank_sum = 0.0

        for j in inbound_nodes:
            out_nodes = list(g.out_degree(j))
            if len(out_nodes) > 0:
                rank_sum += PR[j] / len(out_nodes)

        new_PR[node] = (1 - alpha) * rank_sum + (alpha / n)

    return new_PR
