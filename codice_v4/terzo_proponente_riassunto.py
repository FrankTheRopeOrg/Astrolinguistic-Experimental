"""
Riassunto del terzo proponente (Tabella 6 e Figura 7 della revisione)
=====================================================================
Dopo aver lanciato

    python condizioni.py --braccio llm --modello gpt-4o-mini --semi 30

questo script legge i due file prodotti nella cartella corrente
  risultati_condizioni_llm_<modello>_v3.csv
  proposte_raw_<modello>_v3.jsonl
e stampa tutto cio' che serve per la riga di Tabella 6 e la barra di Figura 7:
  - esiti NUR e GUMO (GIUSTA / CANGURO / SOTTODETERMINATA / irrisolta), copertura hard
  - risposte senza lista parsabile, candidati compilati, coerenti col log (precisione)
  - scambi per run
  - lo stesso replay con il parser tollerante (colonna ombreggiata di Figura 7)
Il replay ripercorre il pipeline in modo deterministico (parlante SIM) usando le
risposte grezze archiviate: con il parser v3 deve riprodurre il CSV esattamente
(viene verificato). Nessuna chiamata API.

Uso: python terzo_proponente_riassunto.py --modello gpt-4o-mini
"""
import argparse
import collections
import csv
import json

import condizioni as C
from replay_proposer import parser_tollerante


class Replay:
    def __init__(self, jsonl, parser):
        self.righe = [json.loads(l) for l in open(jsonl, encoding="utf-8")]
        self.k = 0
        self.parser = parser
        self.stat = collections.Counter()

    ESEMPI = {"v3": {"cong:colore=rosso&moto=rapido", "rel_n:>", "cambio:moto=cambiato",
                     "or:(forma=triangolo&parita=dispari)|(forma=cerchio&parita=pari)"},
              "v4": {"cong:colore=blu&forma=triangolo", "rel_n:<", "cambio:colore=uguale",
                     "or:(forma=cerchio&moto=fermo)|(colore=rosso&parita=pari)"}}

    def proponi(self, parola, osservazioni):
        if self.k >= len(self.righe):
            raise SystemExit("Errore: il file jsonl ha meno risposte del previsto "
                             "(e' stato lanciato piu' volte o interrotto?).")
        r = self.righe[self.k]; self.k += 1
        if r["parola"] != parola:
            raise SystemExit(f"Errore: attesa la parola {parola}, trovata {r['parola']} "
                             f"alla risposta {self.k}: il jsonl non e' in ordine di campagna "
                             "(se hai lanciato condizioni.py piu' volte, cancella il jsonl e rilancia).")
        dati = self.parser(r["risposta_raw"])
        self.stat["risposte"] += 1
        if r.get("stop_reason") in ("length", "max_tokens"):
            self.stat["troncate"] += 1
        if dati is None:
            self.stat["senza_lista"] += 1
            return []
        cand = [c for c in (C.compila_candidato(x) for x in dati) if c is not None]
        self.stat["candidati_grezzi"] += len(dati)
        self.stat["compilati"] += len(cand)
        self.stat["coerenti"] += sum(1 for h in cand if all(
            h.vale(p, s) == pres for (p, s, pres) in osservazioni))
        esempi = self.ESEMPI[C.VERSIONE_PROTOCOLLO]
        self.stat["copie_esempi"] += sum(1 for h in cand if h.descr in esempi)
        if cand and all(h.descr in esempi for h in cand):
            self.stat["risposte_solo_esempi"] += 1
        return cand


def replay(jsonl, parser, semi):
    prop = Replay(jsonl, parser)
    esiti = {w: collections.Counter() for w in sorted(C.REGOLE_VERE)}
    scambi = []
    for seed in range(semi):
        app = C.ApprendistaSeq(C.ParlanteSimSeq(C.verita_L2D), C.spazio_base(),
                               seed=seed, proponente=prop)
        app.fase_ostensione(); app.fase_probing(); app.fase_proposte()
        for w in esiti:
            esiti[w][app.esito(w)] += 1
        scambi.append(app.scambi)
    return esiti, prop.stat, scambi


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modello", default="gpt-4o-mini")
    ap.add_argument("--semi", type=int, default=30)
    ap.add_argument("--versione", choices=["v3", "v4"], default="v3",
                    help="versione dello strumento con cui e' stata fatta la campagna")
    args = ap.parse_args()
    C.imposta_versione(args.versione)
    csv_file = f"risultati_condizioni_llm_{args.modello}_{args.versione}.csv"
    jsonl = f"proposte_raw_{args.modello}_{args.versione}.jsonl"

    # --- 1. esiti dal CSV ---------------------------------------------------
    rows = list(csv.DictReader(open(csv_file, encoding="utf-8")))
    per_parola = collections.defaultdict(collections.Counter)
    for r in rows:
        per_parola[r["parola"]][r["esito"]] += 1
    semi_csv = len({r["seed"] for r in rows})
    print(f"=== {args.modello}: esiti dal CSV ({semi_csv} semi) ===")
    print(f"{'parola':6s} {'GIUSTE':>7s} {'CANGURI':>8s} {'SOTTOD.':>8s} {'irris.':>7s}")
    for w in sorted(per_parola):
        c = per_parola[w]
        print(f"{w:6s} {c['GIUSTA']:>7d} {c['CANGURO']:>8d} {c['SOTTODETERMINATA']:>8d} "
              f"{c['irrisolta']:>7d}" + ("   <- parola difficile" if w in ("NUR", "GUMO") else ""))
    nur, gumo = per_parola["NUR"]["GIUSTA"], per_parola["GUMO"]["GIUSTA"]
    kang = sum(c["CANGURO"] for c in per_parola.values())
    sc = [int(r["scambi_run"]) for r in rows if r["parola"] == "NUR"]
    import statistics
    print(f"\nRIGA TABELLA 6 (parser v3): NUR {nur}/{semi_csv} | GUMO {gumo}/{semi_csv} | "
          f"hard total {100 * (nur + gumo) / (2 * semi_csv):.0f}% | kangaroos {kang} | "
          f"exchanges {statistics.mean(sc):.1f} ± {statistics.stdev(sc):.2f}")

    # --- 2. replay con parser v3 (verifica) e tollerante ---------------------
    for nome, parser in (("parser v3", C._estrai_lista_json), ("parser tollerante", parser_tollerante)):
        esiti, stat, scambi = replay(jsonl, parser, args.semi)
        n, g = esiti["NUR"]["GIUSTA"], esiti["GUMO"]["GIUSTA"]
        k = sum(esiti[w]["CANGURO"] for w in esiti)
        print(f"\n[{nome}] NUR {n}/{args.semi}  GUMO {g}/{args.semi}  hard {100*(n+g)/(2*args.semi):.0f}%  "
              f"kangaroos {k}")
        print(f"   risposte senza lista parsabile {stat['senza_lista']}/{stat['risposte']} "
              f"(troncate a max_tokens: {stat['troncate']}), "
              f"candidati compilati {stat['compilati']}/{stat['candidati_grezzi']}, "
              f"coerenti col log {stat['coerenti']}/{stat['compilati']} "
              f"(precisione {100 * stat['coerenti'] / max(1, stat['compilati']):.0f}%)")
        print(f"   candidati che sono copie letterali degli esempi del prompt: "
              f"{stat['copie_esempi']}/{stat['compilati']} "
              f"({100 * stat['copie_esempi'] / max(1, stat['compilati']):.0f}%); "
              f"risposte fatte SOLO di esempi: {stat['risposte_solo_esempi']}/{stat['risposte']}")
        if nome == "parser v3":
            ok = (n == nur and g == gumo and k == kang)
            print("   replay riproduce il CSV:", "SI" if ok else "NO (controlla che il jsonl sia di questa campagna)")
