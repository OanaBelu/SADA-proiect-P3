"""Rutele principale și rutele de rezervă (partea „precalculată” a nivelului 2).
TODO (GHID.md, pasul 3)."""
from __future__ import annotations

import networkx as nx

from .graph_io import path_edges


def primary_route(G, o, d, weight: str = "length") -> list:
    """Drumul minim, ca listă de noduri (gata)."""
    return nx.shortest_path(G, o, d, weight=weight)


def backup_route(G, o, d, primary: list, weight: str = "length") -> list | None:
    """O rută de rezervă fără muchii comune cu `primary`, sau None dacă nu există.

    TODO: două variante, alegeți una și spuneți în raport:
      - eliminați temporar muchiile rutei principale (path_edges(G, primary)) dintr-o
        copie a grafului (sau folosiți nx.restricted_view) și căutați din nou drumul minim;
      - nx.edge_disjoint_paths(G, o, d) dă drumuri fără muchii comune, dar nu neapărat scurte.
    """
     # strazile de ascuns: cele din ruta principala, in ambele sensuri
    ascunse = []
    for u, v, _ in path_edges(G, primary, weight):
        for a, b in ((u, v), (v, u)):
            if G.has_edge(a, b):
              ascunse += [(a, b, k) for k in G[a][b]]
    H = nx.restricted_view(G, nodes=[], edges=ascunse)
    try:
        return nx.shortest_path(H, o, d, weight=weight)
    except nx.NetworkXNoPath:
        return None

def precompute(G, pairs, weight: str = "length") -> dict:
    """{(o, d): {"primary": [...], "primary_edges": set(...), "backup": [...] | None,
                 "backup_edges": set(...)}}  TODO."""
    raise NotImplementedError("precompute (GHID.md, pasul 3)")


__all__ = ["primary_route", "backup_route", "precompute", "path_edges"]
