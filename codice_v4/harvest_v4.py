"""Raccoglie in un unico JSON tutti i dati delle figure/tabelle della revisione."""
import csv
import json
import statistics
from collections import defaultdict

import trappole as T
from orchestratore import Orchestratore, ParlanteSim, verita_L2, REFERENTI_VERI_L2

D = {}

# ---- campagna 2x2 W32, v4 e v3 (dal CSV di campagna2.py) ----
rows = list(csv.DictReader(open("risultati_campagna2_v3_v4.csv")))
four = defaultdict(lambda: defaultdict(list))
for r in rows:
    for k in ("giuste", "sottod", "occam_ko", "canguri", "irrisolte", "scambi", "rec_r2"):
        four[r["versione"] + "/" + r["condizione"]][k].append(int(r[k]))
D["four_arm"] = {k: dict(v) for k, v in four.items()}

# ---- trappole (v4) con tempi di rilevazione ----
D["traps"] = {}
for nome_t in ("zumu_forma", "tin_moto"):
    t = T.TRAPPOLE[nome_t]
    parola_t, esca = t["parola"], t["esca"]
    pool = T.pool_trappola(parola_t, esca)
    bracci = {
        "A naive": lambda s: T.braccio_ingenuo(s, pool, parola_t, 60),
        "B statistical": lambda s: T.braccio_statistico(s, pool, parola_t, esca, 60),
        "C full, weak": lambda s: T.braccio_completo(s, pool, parola_t, esca, forte=False),
        "C full, strong": lambda s: T.braccio_completo(s, pool, parola_t, esca, forte=True),
    }
    D["traps"][nome_t] = {"pool": len(pool)}
    for nome, run in bracci.items():
        R = [run(s) for s in range(50)]
        counts = {"correct": sum(1 for r in R if r["esito"].startswith("GIUSTA")),
                  "kangaroo": sum(1 for r in R if r["esito"].startswith("CANGURO")),
                  "underdet": sum(1 for r in R if r["esito"].startswith("SOTTO")),
                  "unresolved": sum(1 for r in R if r["esito"].startswith("irrisolta")),
                  "unresolved_right": sum(1 for r in R if r["esito"] == "irrisolta (referente giusto)")}
        det = [r["rilevazione"] for r in R if r["rilevazione"] is not None]
        entry = {"counts": counts, "detections": det,
                 "exchanges": [r["scambi"] for r in R]}
        if "tutte" in R[0]:
            entry["all_words"] = {k: sum(r["tutte"][k] for r in R)
                                  for k in ("giuste", "sottodeterminate", "canguri_residui", "irrisolte")}
        D["traps"][nome_t][nome] = entry

# ---- rumore (v4) ----
rows = list(csv.DictReader(open("risultati_rumore2_v4.csv")))
noise = defaultdict(lambda: defaultdict(list))
for r in rows:
    for k in ("fedelta", "giuste", "sottod", "canguri", "irrisolte", "revocate", "vuote", "scambi"):
        noise[r["p"]][k].append(float(r[k]))
D["noise"] = {k: dict(v) for k, v in noise.items()}

# ---- mondi grandi (v4) ----
rows = list(csv.DictReader(open("risultati_mondi_grandi_v4_part1.csv"))) + \
       list(csv.DictReader(open("risultati_mondi_grandi_v4_part2.csv")))
worlds = defaultdict(lambda: defaultdict(list))
meta = {}
for r in rows:
    key = r["mondo"] + "/" + r["condizione"]
    meta[r["mondo"]] = {"scene": int(r["scene"]), "ipotesi": int(r["ipotesi"]), "parole": int(r["parole"])}
    for k in ("giuste", "sottodeterminate", "canguri", "irrisolte", "irrisolte_giuste",
              "scambi", "rec_r2", "valutazioni", "secondi", "mai_udite"):
        worlds[key][k].append(float(r[k]))
D["worlds"] = {k: dict(v) for k, v in worlds.items()}
D["worlds_meta"] = meta

# ---- sweep round (v4) ----
rows = list(csv.DictReader(open("risultati_sweep_round_v4.csv")))
sweep = defaultdict(lambda: defaultdict(list))
for r in rows:
    key = f"{r['mondo']}/{r['politica']}/{r['round_max']}"
    for k in ("giuste", "canguri", "sottodeterminate", "scambi", "irrisolte"):
        sweep[key][k].append(float(r[k]))
D["sweep"] = {k: dict(v) for k, v in sweep.items()}

# ---- proposer (archivio v3, CSV del repo) ----
prop = {}
for nome, f in (("base", "risultati_condizioni_base_v3.csv"),
                ("oracle", "risultati_condizioni_esteso_v3.csv"),
                ("haiku", "risultati_condizioni_llm_claude-haiku-4-5_v3.csv"),
                ("sonnet", "risultati_condizioni_llm_claude-sonnet-4-6_v3.csv")):
    rows = list(csv.DictReader(open("../results/" + f)))
    c = defaultdict(lambda: defaultdict(int))
    for r in rows:
        c[r["parola"]][r["esito"]] += 1
    prop[nome] = {w: dict(v) for w, v in c.items()}
    prop[nome]["scambi"] = statistics.mean(int(r["scambi_run"]) for r in rows if r["parola"] == "NUR")
D["proposer"] = prop
D["proposer_replay"] = {"haiku_v3": {"NUR": 10, "GUMO": 1, "no_list": 28, "compiled": 98, "coherent": 11},
                        "haiku_lenient": {"NUR": 15, "GUMO": 1, "no_list": 4, "compiled": 156, "coherent": 16},
                        "sonnet_v3": {"NUR": 28, "GUMO": 15, "no_list": 6, "compiled": 97, "coherent": 43},
                        "sonnet_lenient": {"NUR": 28, "GUMO": 15, "no_list": 6, "compiled": 97, "coherent": 43}}

json.dump(D, open("data_v4.json", "w"), indent=1)
print("saved data_v4.json")
for k in D["traps"]:
    print(k, {a: D["traps"][k][a]["counts"] for a in D["traps"][k] if a != "pool"})
    print("   detections mean:", {a: round(statistics.mean(D["traps"][k][a]["detections"]), 1)
                                   for a in D["traps"][k] if a != "pool" and D["traps"][k][a]["detections"]})
    print("   exchanges mean:", {a: round(statistics.mean(D["traps"][k][a]["exchanges"]), 1)
                                 for a in D["traps"][k] if a != "pool"})
