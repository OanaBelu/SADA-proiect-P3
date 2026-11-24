# P3. Toleranță ierarhică la defectare pe rețeaua rutieră a Timișoarei

Proiect la **Sisteme autoadaptive. Design și aplicații**.

Pe harta centrului Timișoarei se închid străzi (aleator, țintit sau în grup: inundație, poduri, axa centrală). Un controller MAPE-K recuperează călătoriile pe trei niveluri:

1. **detecție**: găsește perechile OD care trec pe străzile căzute;
2. **corecție**: le mută pe ruta de rezervă calculată dinainte;
3. **degradare controlată**: dacă nu există rezervă, servește doar perechile prioritare (spre spitale).

Separat, o buclă Langton care se autoreplică, comparată cu refacerea unei rute.

## Instalare

```powershell
powershell -ExecutionPolicy Bypass -File setup\setup.ps1
.\.venv\Scripts\Activate.ps1
```

## Comenzi

```powershell
python scripts\inspect_graph.py data\p3_retea\retea.graphml   # verifică graful, desen în results/figures/network.pdf
python scripts\prepare_od.py                                  # perechile OD -> data/od_pairs.csv
python scripts\harta_spitale.py                               # harta cu spitalele -> results/figures/harta_spitale.pdf / .png
pytest -q                                                     # toate testele
```

Defectele (`failures.py`), câte unul:

```powershell
pytest -v -k random                                           # random_failures: străzi alese la întâmplare
pytest -v -k targeted                                         # targeted_failures: cele mai importante străzi
```

## Date

Rețeaua: 1141 de intersecții și 2865 de străzi, din OpenStreetMap. Perechile OD: 300 eșantionate după populație + 36 prioritare, seed 42. Sursele și licențele sunt în `data/DATA.md`.

## Pornit din

Kitul de pornire P3 și resursele cursului.

## Ce am adăugat

- datele din resursele cursului, instalate cu `instaleaza.py` (`data/p3_retea/`, `data/ca/`);
- perechile OD generate cu `scripts/prepare_od.py` și fixate (`data/od_pairs.csv`);
- harta cu spitalele: `scripts/harta_spitale.py` → `results/figures/harta_spitale.pdf` / `.png`;
- rutele principale și de rezervă, fără străzi comune, în niciun sens: `src/sada/p3/routes.py` (`backup_route`, `precompute`);
- defectele aleatoare, țintite și în grup: `src/sada/p3/failures.py` (`random_failures`, `targeted_failures`, `group_failure`);
- planul de implementare: `docs/P3_Implementare.pdf`.
