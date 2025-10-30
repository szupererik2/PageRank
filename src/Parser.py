from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

from src.Graph import Graph


def find_py_files(root: str):
    for dp, dirs, files in os.walk(root):
        if any(x in dp for x in (os.sep + '.venv', os.sep + 'venv', os.sep + '.git', os.sep + '__pycache__')):
            continue
        for f in files:
            if f.endswith('.py'):
                yield os.path.join(dp, f)


def modulename(root: str, filepath: str) -> str:
    p = Path(filepath).resolve()
    r = Path(root).resolve()
    try:
        rel = p.relative_to(r)
    except Exception:
        return p.stem
    parts = list(rel.with_suffix('').parts)
    if parts and parts[-1] == '__init__':
        parts = parts[:-1]
    return '.'.join(parts) if parts else p.stem

def build_graph(root: str) -> Graph:
    return build_graph_regex(root)


def build_graph_regex(root: str) -> Graph:
    import re

    func_def_re = re.compile(r'^\s*def\s+(\w+)\s*\(')
    class_def_re = re.compile(r'^\s*class\s+(\w+)\s*[:\(]')
    call_re = re.compile(r'([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\(')

    defs: Dict[str, Tuple[str, str, int]] = {}
    calls_in_func: Dict[str, List[Tuple[str, List[str]]]] = {}

    for fp in find_py_files(root):
        try:
            raw = open(fp, 'r', encoding='utf-8').read()
        except Exception:
            continue
        raw_nostr = re.sub(r"(\"\"\".*?\"\"\"|''' .*?'''|\".*?\"|'.*?')", '', raw, flags=re.S)
        lines = raw_nostr.splitlines()
        module = modulename(root, fp)

        class_stack: List[Tuple[str, int]] = []
        func_stack: List[Tuple[str, int]] = []

        for lineno, line in enumerate(lines, start=1):
            m = class_def_re.match(line)
            if m:
                indent = len(line) - len(line.lstrip(' '))
                class_stack.append((m.group(1), indent))
                continue
            cur_indent = len(line) - len(line.lstrip(' '))
            while class_stack and cur_indent <= class_stack[-1][1] and line.strip():
                class_stack.pop()

            mf = func_def_re.match(line)
            if mf:
                fname = mf.group(1)
                qual_parts = [c for c, _ in class_stack] + [fname]
                qual = '.'.join(qual_parts) if qual_parts else fname
                fq = f"{module}:{qual}"
                defs[fq] = (module, qual, lineno)
                func_stack.append((fq, len(line) - len(line.lstrip(' '))))
                calls_in_func.setdefault(fp, []).append((fq, []))
                continue
            if func_stack:
                f_indent = func_stack[-1][1]
                if cur_indent <= f_indent and line.strip():
                    func_stack.pop()
                else:
                    for callm in call_re.finditer(line):
                        call_name = callm.group(1)
                        if calls_in_func.get(fp):
                            calls_in_func[fp][-1][1].append(call_name)

    name_to_fqs: Dict[str, List[str]] = {}
    for fq in defs:
        short = fq.split(':', 1)[1].split('.')[-1]
        name_to_fqs.setdefault(short, []).append(fq)

    g = Graph()
    for fq in defs:
        g.add_node(fq)

    for fp, funcs in calls_in_func.items():
        module = modulename(root, fp)
        for fqcaller, call_list in funcs:
            for called in call_list:
                tail = called.split('.')[-1]
                resolved = None
                candidates = name_to_fqs.get(tail, [])
                if len(candidates) == 1:
                    resolved = candidates[0]
                else:
                    for c in candidates:
                        if c.startswith(module + ':'):
                            resolved = c
                            break
                    if not resolved and candidates:
                        resolved = candidates[0]

                if resolved and resolved != fqcaller:
                    try:
                        g.add_edge(fqcaller, resolved)
                    except Exception:
                        pass

    return g


if __name__ == '__main__':
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    root = os.path.abspath(root)
    g = build_graph(root)
    print(len(g.adj_list))
    print(sum(len(v) for v in g.adj_list.values()))
