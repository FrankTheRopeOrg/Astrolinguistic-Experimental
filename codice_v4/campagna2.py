"""Campagna 2x2 con metrica per classi, per protocollo v3 (archiviato) e v4
(Eq. 2 a ogni scambio). Scrive un CSV per run."""
import csv
import statistics
import sys
from orchestratore import Orchestratore, ParlanteSim, verita_L2

CONDIZIONI = [("Random", False, False), ("Random+R2", False, True),
              ("Active", True, False), ("Active+R2", True, True)]

def un_run(seed, attiva, round2, condivisione):
    Orchestratore.CONDIVISIONE = condivisione
    orch = Orchestratore(ParlanteSim(verita_L2), seed=seed, attiva=attiva,
                         logfile="tmp.jsonl")
    orch.fase_ostensione(n_scene=6)
    orch.fase_coppie_minime()
    orch.fase_probing(round_n=1)
    if round2:
        orch.fase_probing(round_n=2)
    orch.log.close()
    m = orch.metriche()
    return {"seed": seed, "giuste": m["giuste"], "sottod": m["sottodeterminate"],
            "occam_ko": m["occam_errato"], "canguri": m["canguri_residui"],
            "irrisolte": m["irrisolte"], "scambi": m["scambi_totali"],
            "rec_r2": m["promosse_per_round"].get(2, 0)}

def ms(v):
    return f"{statistics.mean(v):.2f} ± {statistics.stdev(v):.2f}"

if __name__ == "__main__":
    semi = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    righe = []
    for versione, cond in (("v3", False), ("v4", True)):
        print(f"\n=== protocollo {versione} ({'Eq.2 a ogni scambio' if cond else 'archiviato'}) ===")
        print(f"{'condizione':11s} {'corrette':>13s} {'sottodet.':>13s} {'occamKO':>8s} "
              f"{'canguri':>13s} {'irrisolte':>13s} {'scambi':>13s} {'recR2':>6s}")
        for nome, attiva, r2 in CONDIZIONI:
            R = [un_run(s, attiva, r2, cond) for s in range(semi)]
            for r in R:
                righe.append({"versione": versione, "condizione": nome, **r})
            print(f"{nome:11s} {ms([r['giuste'] for r in R]):>13s} "
                  f"{ms([r['sottod'] for r in R]):>13s} "
                  f"{sum(r['occam_ko'] for r in R):>8d} "
                  f"{ms([r['canguri'] for r in R]):>13s} "
                  f"{ms([r['irrisolte'] for r in R]):>13s} "
                  f"{ms([r['scambi'] for r in R]):>13s} "
                  f"{sum(r['rec_r2'] for r in R):>6d}")
    with open("risultati_campagna2_v3_v4.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader(); w.writerows(righe)
