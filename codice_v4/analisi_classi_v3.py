"""Riclassifica gli esiti della campagna 2x2 (v3 archiviata) con la metrica
per classi (Eq. 6): quante promozioni avvengono con rivali superstiti, e in
quante di esse la scelta di Occam sarebbe sbagliata."""
import statistics
from orchestratore import Orchestratore, ParlanteSim, verita_L2, REFERENTI_VERI_L2

def run(seed, attiva, round2):
    orch = Orchestratore(ParlanteSim(verita_L2), seed=seed, attiva=attiva,
                         logfile="tmp.jsonl")
    orch.fase_ostensione(n_scene=6)
    orch.fase_coppie_minime()
    orch.fase_probing(round_n=1)
    if round2:
        orch.fase_probing(round_n=2)
    orch.log.close()
    out = {"corrette": 0, "sottod_occam_ok": 0, "sottod_occam_ko": 0,
           "canguri_vera_esclusa": 0, "irrisolte": 0, "scambi": orch.scambi}
    for w, a in orch.ancore.items():
        vera = frozenset(REFERENTI_VERI_L2[w])
        sup = {frozenset(h) for h in a.ipotesi}
        if a.stato != "PROMOSSA" or not sup:
            out["irrisolte"] += 1
        elif vera not in sup:
            out["canguri_vera_esclusa"] += 1
        elif len(sup) == 1:
            out["corrette"] += 1
        else:
            if frozenset(a.referente_stimato()) == vera:
                out["sottod_occam_ok"] += 1
            else:
                out["sottod_occam_ko"] += 1
    return out

for nome, attiva, r2 in [("Random", False, False), ("Random+R2", False, True),
                         ("Active", True, False), ("Active+R2", True, True)]:
    R = [run(s, attiva, r2) for s in range(50)]
    agg = {k: sum(r[k] for r in R) for k in R[0]}
    print(f"{nome:10s} " + " ".join(f"{k}={agg[k]}" for k in agg if k != "scambi")
          + f" scambi={statistics.mean(r['scambi'] for r in R):.1f}")
