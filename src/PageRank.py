import Graph

alpha = 0.15

def RankCalc(g, PR):
    new_PR = {}
    nodes = g.get_nodes()
    n = len(nodes)

    for node in nodes:
        inbound_nodes = g.in_degree(node)
        rank_sum = 0.0

        for j in inbound_nodes:
            out_degree = g.out_degree(j)
            if len(out_degree) > 0:
                rank_sum += PR[j] / len(out_degree)

        new_PR[node] = (1 - alpha) * rank_sum + (alpha / n)

    return new_PR


def RankPage(g):
    if not hasattr(g, 'get_nodes') or not callable(getattr(g, 'get_nodes')):
        raise TypeError("RankPage's parameter must be a graph-like object with a get_nodes() method")
    
    nodes = g.get_nodes()
    if not nodes:
        return {}

    PR = {}
    init_value = 1.0 / len(nodes)
    for n in nodes:
        PR[n] = init_value

    newPR = RankCalc(g,PR)
    
    epsilon = 1e-6
    max_iter = 100

    for _ in range(max_iter):
        delta = sum(abs(newPR[n] - PR[n]) for n in nodes)
        PR = newPR
        if delta < epsilon:
            break
        newPR = RankCalc(g, PR)
    
    return PR
    