from __future__ import annotations

import ast, os, sys, warnings
from pathlib import Path
from typing import Dict, List, Tuple

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
from src.Graph import Graph

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

def find_py_files(root: str):
    for dp, dirs, files in os.walk(root):
        if any(x in dp for x in (os.sep + '.venv', os.sep + 'venv', os.sep + '.git', os.sep + '__pycache__')):
            continue
        for f in files:
            if f.endswith('.py'):
                yield os.path.join(dp, f)

def expr_to_name(expr):
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        parts = []
        cur = expr
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            return '.'.join(reversed(parts))
    return None

def collect_defs(root: str) -> Dict[str, Tuple[str, str, int]]:
    defs: Dict[str, Tuple[str, str, int]] = {}
    for fp in find_py_files(root):
        try:
            src = open(fp, 'r', encoding='utf-8').read()
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', SyntaxWarning)
                tree = ast.parse(src, filename=fp)
        except Exception:
            continue
        module = modulename(root, fp)
        stack: List[str] = []
        class V(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                qual = '.'.join(stack + [node.name]) if stack else node.name
                fq = f"{module}:{qual}"
                defs[fq] = (module, qual, node.lineno)
                stack.append(node.name)
                self.generic_visit(node)
                stack.pop()
            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)
            def visit_ClassDef(self, node):
                stack.append(node.name)
                self.generic_visit(node)
                stack.pop()
        V().visit(tree)
    return defs

def build_graph(root: str) -> Graph:
    defs = collect_defs(root)
    name_to_fqs: Dict[str, List[str]] = {}
    for fq in defs:
        name = fq.split(':',1)[1].split('.')[-1]
        name_to_fqs.setdefault(name, []).append(fq)
    g = Graph()
    for fq in defs:
        g.add_node(fq)
    for fp in find_py_files(root):
        try:
            src = open(fp, 'r', encoding='utf-8').read()
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', SyntaxWarning)
                tree = ast.parse(src, filename=fp)
        except Exception:
            continue
        module = modulename(root, fp)
        stack: List[str] = []
        class C(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                qual = '.'.join(stack + [node.name]) if stack else node.name
                caller = f"{module}:{qual}"
                stack.append(node.name)
                for n in ast.walk(node):
                    if isinstance(n, ast.Call):
                        nm = expr_to_name(n.func)
                        if not nm:
                            continue
                        resolved = None
                        if '.' in nm:
                            tail = nm.split('.')[-1]
                            candidates = name_to_fqs.get(tail, [])
                            if len(candidates) == 1:
                                resolved = candidates[0]
                            else:
                                for c in candidates:
                                    if c.startswith(module+':'):
                                        resolved = c
                                        break
                                if not resolved and candidates:
                                    resolved = candidates[0]
                        else:
                            candidates = name_to_fqs.get(nm, [])
                            if len(candidates) == 1:
                                resolved = candidates[0]
                            else:
                                for c in candidates:
                                    if c.startswith(module+':'):
                                        resolved = c
                                        break
                                if not resolved and candidates:
                                    resolved = candidates[0]
                        if resolved and resolved != caller:
                            try:
                                g.add_edge(caller, resolved)
                            except Exception:
                                pass
                self.generic_visit(node)
                stack.pop()
            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)
            def visit_ClassDef(self, node):
                stack.append(node.name)
                self.generic_visit(node)
                stack.pop()
        C().visit(tree)
    return g

def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    root = os.path.abspath(root)
    g = build_graph(root)
    print(len(g.get_nodes()))
    total_edges = sum(len(v) for v in g.adj_list.values())
    print(total_edges)

if __name__ == '__main__':
    main(sys.argv)
