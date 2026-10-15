"""Campagna su mondi di dimensione crescente (protocollo v4), 2x2 condizioni."""
import csv
import statistics
import sys
import time
from mondo import Mondo, MONDO_ORIGINALE, run

MONDI = {
    "W32":   dict(attributi={"forma": ["triangolo", "cerchio"],
                             "colore": ["rosso", "blu"],
                             "moto": ["rapido", "fermo"]}, n_max=4),
    "W162":  dict(attributi={"forma": ["triangolo", "cerchio", "quadrato"],
                             "colore": ["rosso", "blu", "verde"],
                             "moto": ["rapido", "fermo", "lento"]}, n_max=6),
    "W486":  dict(attributi={"forma": ["triangolo", "cerchio", "quadrato"],
                             "colore": ["rosso", "blu", "verde"],
                             "moto": ["rapido", "fermo", "lento"],
                             "taglia": ["piccolo", "medio", "grande"]}, n_max=6),
    "W2048": dict(attributi={"forma": ["triangolo", "cerchio", "quadrato", "stella"],
                             "colore": ["rosso", "blu", "verde", "giallo"],
                             "moto": ["rapido", "fermo", "lento", "oscillante"],
                             "taglia": ["piccolo", "medio", "grande", "enorme"]}, n_max=8),
}
CONDIZIONI = [("Random", False, False), ("Active", True, False),
              ("Random+R2", False, True), ("Active+R2", True, True)]

def ms(v, f="{:.2f}"):
    return (f + " ± " + f).format(statistics.mean(v), statistics.stdev(v))

if __name__ == "__main__":
    semi = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    quali = sys.argv[2].split(",") if len(sys.argv) > 2 else list(MONDI)
    righe = []
    for nome_m in quali:
        m = Mondo(**MONDI[nome_m])
        print(f"\n=== {nome_m}: {len(m.scene)} scene, {len(m.ipotesi_universo)} ipotesi H0, "
              f"{len(m.referenti)} parole L2, {len(m.atomi)} atomi ===")
        print(f"{'condizione':10s} {'corrette':>13s} {'sottod':>12s} {'occamKO':>7s} {'canguri':>12s} "
              f"{'irrisolte':>13s} {'irr.giuste':>10s} {'mai udite':>9s} {'scambi':>15s} "
              f"{'recR2':>5s} {'s/run':>6s} {'valut/run':>10s}")
        for nome_c, att, r2 in CONDIZIONI:
            t0 = time.perf_counter()
            R = [run(m, s, att, r2) for s in range(semi)]
            for r in R:
                righe.append({"mondo": nome_m, "scene": len(m.scene),
                              "ipotesi": len(m.ipotesi_universo),
                              "parole": len(m.referenti), "condizione": nome_c, **r})
            print(f"{nome_c:10s} {ms([r['giuste'] for r in R]):>13s} "
                  f"{ms([r['sottodeterminate'] for r in R]):>12s} "
                  f"{sum(r['occam_errato'] for r in R):>7d} "
                  f"{ms([r['canguri'] for r in R]):>12s} "
                  f"{ms([r['irrisolte'] for r in R]):>13s} "
                  f"{sum(r['irrisolte_giuste'] for r in R):>10d} "
                  f"{sum(r['mai_udite'] for r in R):>9d} "
                  f"{ms([r['scambi'] for r in R], '{:.1f}'):>15s} "
                  f"{sum(r['rec_r2'] for r in R):>5d} "
                  f"{(time.perf_counter() - t0) / semi:>6.2f} "
                  f"{statistics.mean(r['valutazioni'] for r in R):>10.0f}")
    with open("risultati_mondi_grandi_v4.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader(); w.writerows(righe)
