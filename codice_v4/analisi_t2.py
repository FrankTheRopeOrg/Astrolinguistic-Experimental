"""Diagnosi degli esiti SOTTODETERMINATA nella trappola tin_moto, C-debole."""
import json
from trappole import (TRAPPOLE, pool_trappola, OrchestratoreTrappola,
                      esito_classe)
from orchestratore import (ParlanteSim, verita_L2, REFERENTI_VERI_L2,
                           Scena, _vale)

t = TRAPPOLE["tin_moto"]
parola_t, esca = t["parola"], t["esca"]
pool = pool_trappola(parola_t, esca)
vera = REFERENTI_VERI_L2[parola_t]

sottod = []
for seed in range(50):
    p2 = ParlanteSim(verita_L2)
    orch = OrchestratoreTrappola(p2, pool, parola_t, esca, forte=False,
                                 seed=seed, attiva=True,
                                 logfile=f"log_t2_seed{seed}.jsonl")
    orch.fase_ostensione(n_scene=6)
    orch.fase_coppie_minime()
    orch.fase_probing(round_n=1)
    orch.fase_probing(round_n=2)
    orch.log.close()
    a = orch.ancore[parola_t]
    es = esito_classe(a.stato, a.ipotesi, a.referente_stimato(), vera)
    if es == "SOTTODETERMINATA":
        # quali scene osservate (nel log) avrebbero eliminato i rivali?
        rivali = [h for h in a.ipotesi if frozenset(h) != frozenset(vera)]
        osservate = []
        for riga in open(f"log_t2_seed{seed}.jsonl", encoding="utf-8"):
            d = json.loads(riga)
            if "scena" in d:
                s = Scena(**d["scena"])
                pres = parola_t in d["risposta_L2"].split()
                osservate.append((s, pres))
        falsificanti = {}
        for h in rivali:
            falsificanti[tuple(sorted(h))] = sum(
                1 for (s, pres) in osservate if _vale(h, s) != pres)
        sottod.append((seed, a.round_promozione, orch.scambi,
                       sorted(tuple(sorted(h)) for h in a.ipotesi),
                       falsificanti, a.probe_ok, a.probe_falliti))

print(f"SOTTODETERMINATA: {len(sottod)}/50")
for seed, rnd, sc, ip, fals, ok, fail in sottod:
    print(f"seed {seed:2d} | promossa al round {rnd} | scambi {sc} | "
          f"probe ok/falliti {ok}/{fail}")
    print(f"   superstiti: {ip}")
    print(f"   scene osservate nel log che falsificano ciascun rivale: {fals}")
