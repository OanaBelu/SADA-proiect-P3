"""Defectele: eliminare aleatoare, țintită după importanță, în grup.
TODO (GHID.md, pasul 5). `edge_importance` e gata."""
from __future__ import annotations

import networkx as nx
import numpy as np


def edge_importance(G, k: int | None = 500, weight: str = "length", seed: int = 0) -> dict:
    """Centralitatea de intermediere a muchiilor (edge betweenness).
    Pe grafuri de mii de noduri, k < număr de noduri face calculul aproximativ
    prin eșantionarea a k noduri sursă; k=None face calculul exact (lent)."""
    k = None if (k is None or k >= G.number_of_nodes()) else k
    return nx.edge_betweenness_centrality(G, k=k, weight=weight, seed=seed)


def random_failures(G, frac: float, rng: np.random.Generator) -> list:
    """Lista muchiilor de eliminat, alese aleator (frac din total). TODO"""
    # toate strazile, mereu in aceeasi ordine
    muchii = sorted(G.edges(keys=True))
    # cate cad: 10 % din 2865 = 287
    n = round(frac * len(muchii))
    # alegem n pozitii diferite, apoi luam strazile de pe ele
    alese = rng.choice(len(muchii), size=n, replace=False)
    return [muchii[i] for i in alese]


def targeted_failures(G, frac: float, importance: dict, recompute: bool = False) -> list:
    """Muchiile cele mai importante, în ordine. Dacă recompute=True, importanța se
    recalculează după fiecare eliminare (mai realist, mult mai lent). TODO"""
    # strazile de la cea mai importanta la cea mai putin importanta
    ordonate = sorted(importance, key=importance.get, reverse=True)
    # cate cad: acelasi procent ca la aleator
    n = round(frac * G.number_of_edges())
    # primele n din lista ordonata
    return ordonate[:n]


def group_failure(G, scenario: dict) -> list:
    """Toate muchiile unui scenariu de defect în grup (din fișierul de sinteză). TODO"""
    raise NotImplementedError
