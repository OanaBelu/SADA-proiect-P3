"""Recuperarea ierarhică pe trei nivele, ca buclă MAPE-K. TODO (GHID.md, pasul 6).

Nivelul 1, detecție:   ce perechi OD au rute care conțin muchii căzute?
Nivelul 2, corecție:   comută pe ruta de rezervă precalculată, dacă e intactă.
Nivelul 3, degradare:  dacă nici rezerva nu merge, recalculează doar pentru
                       perechile prioritare și raportează ce rămâne fără serviciu.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import pandas as pd

from sada.mapek import Controller

from .graph_io import node_key
from .routes import primary_route


@dataclass
class NetworkState:
    """Starea rețelei pe care o gestionează controllerul (gata de folosit).

    G          graful intact (nu se modifică; muchiile căzute sunt doar marcate)
    pairs      perechile OD (DataFrame cu origin, destination, priority)
    routes     dicționarul din routes.precompute: {(o, d): {"primary": [...], "backup": [...] | None, ...}}
    failed     toate muchiile căzute, ca (u, v, cheie)
    new_failures  muchiile căzute de la ultimul ciclu al controllerului (le goliți voi după M)
    current    ruta folosită acum de fiecare pereche (listă de noduri) sau None dacă nu e servită
    level      nivelul care servește perechea: 0 = ruta principală, 2 = rezerva, 3 = recalculată (prioritar)
    """
    G: nx.MultiDiGraph
    pairs: pd.DataFrame
    routes: dict
    failed: set = field(default_factory=set)
    new_failures: set = field(default_factory=set)
    current: dict = field(default_factory=dict)
    level: dict = field(default_factory=dict)

    def __post_init__(self):
        for od, r in self.routes.items():
            self.current.setdefault(od, r["primary"])
            self.level.setdefault(od, 0)

    def od_keys(self):
        """Perechile ca tuple de chei de noduri din graf, cu indicatorul de prioritate."""
        out = []
        for _, r in self.pairs.iterrows():
            out.append(((node_key(self.G, r["origin"]), node_key(self.G, r["destination"])), bool(r.get("priority", False))))
        return out

    def fail(self, edges) -> None:
        edges = set(map(tuple, edges))
        self.new_failures |= edges - self.failed
        self.failed |= edges

    def view(self):
        """Graful fără muchiile căzute (o vedere, fără copiere)."""
        return nx.restricted_view(self.G, nodes=[], edges=list(self.failed))

    def route_ok(self, route) -> bool:
        """Adevărat dacă între fiecare două noduri consecutive există cel puțin o muchie necăzută."""
        if not route:
            return False
        for u, v in zip(route[:-1], route[1:]):
            keys = self.G[u][v].keys() if self.G.is_multigraph() else [None]
            if all(((u, v, k) if k is not None else (u, v)) in self.failed for k in keys):
                return False
        return True

    def served_share(self, priority_only: bool = False) -> float:
        prio = dict(self.od_keys())
        ods = [od for od in self.current if (prio.get(od, False) or not priority_only)]
        if not ods:
            return float("nan")
        return sum(1 for od in ods if self.route_ok(self.current[od])) / len(ods)


class HierarchicalRecovery(Controller):
    """M: muchiile căzute de la ultimul ciclu, componentele conexe.
    A: perechile afectate; tipul defectului (izolat / țintit / în grup), procentul deconectat.
    P: nivelul de răspuns pentru fiecare pereche afectată (1, 2 sau 3) și ruta nouă.
    E: actualizează rutele curente; marchează perechile în serviciu degradat.
    K: rutele principale și de rezervă (routes.precompute), muchiile critice, jurnalul.
    """

    def monitor(self, network, t):
        # strazile inchise de la tura trecuta
        noi = set(network.new_failures)
        # le golesc, ca la tura urmatoare sa ramana doar ce se inchide atunci
        network.new_failures.clear()
        # analyze nu primeste reteaua, asa ca o tin minte in k
        self.k.state["retea"] = network
        # ce s-a inchis acum si cate sunt inchise de la inceput
        return {"noi": noi, "inchise_total": len(network.failed)}

    def analyze(self, measurements, t):
        # daca nu s-a inchis nimic nou, nu am ce cauta
        if not measurements["noi"]:
            return {"afectate": []}
        # iau reteaua pe care a pus-o monitor in k
        network = self.k.state["retea"]
        # calatoriile al caror drum de acum trece pe o strada inchisa
        afectate = [od for od, drum in network.current.items()
                    if drum is not None and not network.route_ok(drum)]
        return {"afectate": afectate}

    def plan(self, assessment, t):
        # daca nu e nicio calatorie afectata, nu am nimic de hotarat
        if not assessment["afectate"]:
            return None

        # iau reteaua pe care a pus-o monitor in k
        network = self.k.state["retea"]
        # calatoriile spre spitale (doar ele primesc nivelul 3)
        prioritare = {od for od, prio in network.od_keys() if prio}
        # aici notez ce hotarasc pentru fiecare calatorie: (calatoria, nivelul, drumul)
        decizii = []
        for od in assessment["afectate"]:
            # drumul b al calatoriei, calculat de precompute in routes.py (None daca nu are)
            rezerva = network.routes[od]["backup"]
            # nivelul 2: drumul b exista si e intreg, merg pe el
            if rezerva is not None and network.route_ok(rezerva):
                decizii.append((od, 2, rezerva))
            # nivelul 3: doar pentru spitale caut un drum nou pe harta ramasa
            elif od in prioritare and nx.has_path(network.view(), *od):
                drum_nou = primary_route(network.view(), *od)
                decizii.append((od, 3, drum_nou))
            # restul raman fara drum (degradarea controlata)
            else:
                decizii.append((od, None, None))
        return {"decizii": decizii} 

    def execute(self, network, action, t):
        raise NotImplementedError
