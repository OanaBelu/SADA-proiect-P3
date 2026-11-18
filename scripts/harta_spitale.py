"""harta retelei cu spitalele si populatia pe intersectii
python scripts/harta_spitale.py"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import LineCollection

from sada.p3.graph_io import load_graph, node_key
from sada.plotting import savefig, setup_style

G = load_graph("data/p3_retea/retea.graphml")
prioritare = pd.read_csv("data/p3_retea/prioritare.csv")
spitale = {node_key(G, n) for n in prioritare["destination"]}

poz = {n: (d["x"], d["y"]) for n, d in G.nodes(data=True)}
pop = [d.get("population", 0) for _, d in G.nodes(data=True)]

setup_style()
fig, ax = plt.subplots(figsize=(8, 8))
strazi = [(poz[u], poz[v]) for u, v in G.edges()]
ax.add_collection(LineCollection(strazi, colors="#9aa5b1", linewidths=0.6))
puncte = ax.scatter(*zip(*poz.values()), s=4, c=pop, cmap="viridis", zorder=2)

ax.scatter(*zip(*(poz[n] for n in spitale)), s=60, marker="P", c="#d62728",
             zorder=3, label="spitale (destinații prioritare)")
fig.colorbar(puncte, ax=ax, shrink=0.6, label="populație estimată pe intersecție")
  # la 45,75 grade latitudine un grad de longitudine e mai scurt, fara corectie harta iese turtita
ax.set_aspect(1 / math.cos(math.radians(45.75)))
ax.autoscale()
ax.set_xlabel("longitudine (°)")
ax.set_ylabel("latitudine (°)")
ax.set_title(f"Centrul Timișoarei: {G.number_of_nodes()} intersecții, {G.number_of_edges()} străzi, 6 spitale")
ax.legend(loc="lower left")

savefig(fig, "results/figures/harta_spitale")
print("salvat results/figures/harta_spitale.pdf si .png")