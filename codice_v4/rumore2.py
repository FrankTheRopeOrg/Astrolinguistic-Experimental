"""Informante rumoroso, protocollo v4 (attiva + R2), esiti per classi."""
import csv
import json
import statistics
import sys
from orchestratore import Orchestratore, ParlanteSim, verita_L2, Scena
from rumore import ParlanteSimRumoroso

def un_run(p, seed, attiva=True, round2=True):
    p2 = ParlanteSim(verita_L2) if p == 0 else ParlanteSimRumoroso(p, seed)
    logfile = f"log_rumore2_p{p}_seed{seed}.jsonl"
    orch = Orchestratore(p2, seed=seed, attiva=attiva, logfile=logfile)
    orch.fase_ostensione(n_scene=6)
    orch.fase_coppie_minime()
    orch.fase_probing(round_n=1)
    if round2:
        orch.fase_probing(round_n=2)
    orch.log.close()
    m = orch.metriche()
    ok = tot = 0
    for riga in open(logfile, encoding="utf-8"):
        d = json.loads(riga)
        if "scena" not in d:
            continue
        tot += 1
        if set(d["risposta_L2"].split()) == set(verita_L2(Scena(**d["scena"])).split()):
            ok += 1
    revocate = sum(1 for a in orch.ancore.values() if a.stato == "REVOCATA")
    irr_giuste = sum(1 for w, a in orch.ancore.items()
                     if a.stato not in ("PROMOSSA",) and
                     {frozenset(h) for h in a.ipotesi} == {frozenset(orch.ancore[w].ipotesi and
                      __import__('orchestratore').REFERENTI_VERI_L2[w])})
    vuote = sum(1 for a in orch.ancore.values() if not a.ipotesi)
    return {"p": p, "seed": seed, "fedelta": 100.0 * ok / tot,
            "giuste": m["giuste"], "sottod": m["sottodeterminate"],
            "canguri": m["canguri_residui"], "irrisolte": m["irrisolte"],
            "revocate": revocate, "vuote": vuote, "scambi": m["scambi_totali"]}

if __name__ == "__main__":
    semi = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    livelli = [0.0, 0.005, 0.01, 0.02, 0.05, 0.10]
    righe = []
    print(f"{'p':>6s} {'fedelta%':>14s} {'giuste':>12s} {'sottod':>12s} {'canguri':>12s} "
          f"{'irrisolte':>12s} {'revocate':>9s} {'vuote':>6s} {'scambi':>8s}  canguri tot")
    for p in livelli:
        R = [un_run(p, s) for s in range(semi)]
        righe += R
        def ms(k):
            v = [r[k] for r in R]
            return f"{statistics.mean(v):.2f} ± {statistics.stdev(v):.2f}"
        fed = [r["fedelta"] for r in R]
        print(f"{p:>6.3f} {statistics.mean(fed):>6.1f} ± {statistics.stdev(fed):<5.1f} "
              f"{ms('giuste'):>12s} {ms('sottod'):>12s} {ms('canguri'):>12s} "
              f"{ms('irrisolte'):>12s} {sum(r['revocate'] for r in R):>9d} "
              f"{sum(r['vuote'] for r in R):>6d} "
              f"{statistics.mean(r['scambi'] for r in R):>8.1f}  {sum(r['canguri'] for r in R)}")
    with open("risultati_rumore2_v4.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader(); w.writerows(righe)
