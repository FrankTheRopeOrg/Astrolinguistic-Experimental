"""Copertura vs scambi: politica casuale con piu' round di recupero contro
politica attiva con un solo round di recupero (parita' di costo)."""
import csv, statistics, sys
from mondo import Mondo, run
from mondi_grandi import MONDI
semi = int(sys.argv[1]) if len(sys.argv) > 1 else 50
righe = []
for nome_m in ["W32", "W162", "W486", "W2048"]:
    m = Mondo(**MONDI[nome_m])
    print(f"\n=== {nome_m} ({len(m.scene)} scene, {len(m.referenti)} parole) ===")
    for pol, att, rounds in [("Random", False, [1, 2, 3, 4, 6]), ("Active", True, [1, 2, 3])]:
        for rmax in rounds:
            R = [run(m, s, att, False, round_max=rmax) for s in range(semi)]
            g = [r["giuste"] for r in R]; sc = [r["scambi"] for r in R]
            k = sum(r["canguri"] for r in R); sd = sum(r["sottodeterminate"] for r in R)
            print(f"{pol:7s} round {rmax}: corrette {statistics.mean(g):5.2f} ± {statistics.stdev(g):4.2f} "
                  f"({100*statistics.mean(g)/len(m.referenti):5.1f}%)  scambi {statistics.mean(sc):6.1f} ± {statistics.stdev(sc):4.1f}"
                  f"  canguri {k}  sottod {sd}")
            for r in R:
                righe.append({"mondo": nome_m, "parole": len(m.referenti), "politica": pol, "round_max": rmax, **r})
with open("risultati_sweep_round_v4.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0])); w.writeheader(); w.writerows(righe)
