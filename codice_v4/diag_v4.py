"""Diagnostica v4: dimensione degli insiemi di ipotesi all'inizio del probing,
probe falliti, cause delle irrisolte."""
import statistics
from collections import Counter
from orchestratore import Orchestratore, ParlanteSim, verita_L2, REFERENTI_VERI_L2

def run(seed, attiva, round2, cond):
    Orchestratore.CONDIVISIONE = cond
    orch = Orchestratore(ParlanteSim(verita_L2), seed=seed, attiva=attiva,
                         logfile="tmp.jsonl")
    orch.fase_ostensione(n_scene=6)
    tag_ost = {w: len(a.ipotesi) for w, a in orch.ancore.items()}
    orch.fase_coppie_minime()
    tag_mp = {w: len(a.ipotesi) for w, a in orch.ancore.items()}
    disc = {w: a.coppie_discriminanti for w, a in orch.ancore.items()}
    orch.fase_probing(round_n=1)
    if round2:
        orch.fase_probing(round_n=2)
    orch.log.close()
    falliti = sum(a.probe_falliti for a in orch.ancore.values())
    irr = [(w, len(a.ipotesi), a.coppie_discriminanti, a.stato)
           for w, a in orch.ancore.items() if a.stato != "PROMOSSA"]
    return tag_ost, tag_mp, disc, falliti, irr

for cond in (False, True):
    print(f"\n=== CONDIVISIONE={cond} ({'v4' if cond else 'v3'}) | Active+R2 ===")
    sizes_ost, sizes_mp, fails, irr_all = [], [], 0, []
    for s in range(50):
        o, m, d, f, irr = run(s, True, True, cond)
        sizes_ost += list(o.values()); sizes_mp += list(m.values())
        fails += f; irr_all += irr
    print("|H| dopo ostensione: media %.2f, distribuzione %s" % (
        statistics.mean(sizes_ost), sorted(Counter(sizes_ost).items())))
    print("|H| dopo coppie minime: media %.2f, distribuzione %s" % (
        statistics.mean(sizes_mp), sorted(Counter(sizes_mp).items())))
    print("probe falliti totali (300 parole):", fails)
    print("irrisolte:", len(irr_all), "di cui con 0 coppie discriminanti:",
          sum(1 for x in irr_all if x[2] == 0),
          "| |H| delle irrisolte:", sorted(Counter(x[1] for x in irr_all).items()))
    print("parole irrisolte:", sorted(Counter(x[0] for x in irr_all).items()))
