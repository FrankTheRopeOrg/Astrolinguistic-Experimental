"""Replay delle risposte GREZZE archiviate del proponente (v3) attraverso il
pipeline di condizioni.py, con (a) il parser v3 originale e (b) un parser
tollerante che recupera i singoli candidati JSON validi anche quando la
lista nel suo insieme e' malformata. Nessuna chiamata API: le risposte
sono quelle archiviate; i log di osservazione sono deterministici (SIM).
Misura quanto della differenza Haiku/Sonnet e' effetto dello STRUMENTO
(parser) e non del modello."""
import json
import re
import sys
import collections
import condizioni as C

REPO = "../logs/proposer/"

def _oggetti_in(blocco: str):
    cands, i = [], 0
    while i < len(blocco):
        if blocco[i] == "{":
            livello = 0
            for j in range(i, len(blocco)):
                if blocco[j] == "{":
                    livello += 1
                elif blocco[j] == "}":
                    livello -= 1
                    if livello == 0:
                        try:
                            d = json.loads(blocco[i:j + 1])
                            if isinstance(d, dict) and "op" in d:
                                cands.append(d)
                        except json.JSONDecodeError:
                            pass
                        i = j
                        break
            else:
                break
        i += 1
    return cands

def parser_tollerante(testo: str):
    """Come il parser v3 (ultima lista JSON bilanciata di candidati); se
    nessuna lista e' parsabile nel suo insieme, recupera dall'ULTIMO blocco
    [...] i singoli oggetti JSON validi con chiave 'op' (un candidato
    malformato non fa perdere gli altri)."""
    v3 = C._estrai_lista_json(testo)
    if v3 is not None:
        return v3
    t = testo.replace("```json", "").replace("```", "")
    blocchi, i = [], 0
    while i < len(t):
        if t[i] == "[":
            livello = 0
            for j in range(i, len(t)):
                if t[j] == "[":
                    livello += 1
                elif t[j] == "]":
                    livello -= 1
                    if livello == 0:
                        blocchi.append(t[i:j + 1]); i = j; break
            else:
                break
        i += 1
    for b in reversed(blocchi):
        ogg = _oggetti_in(b)
        if ogg:
            return ogg
    return None

class ProponenteReplay:
    def __init__(self, modello, parser):
        self.righe = [json.loads(l) for l in open(
            REPO + f"proposte_raw_{modello}_v3.jsonl", encoding="utf-8")]
        self.k = 0
        self.parser = parser
        self.stat = collections.Counter()
    def proponi(self, parola, osservazioni):
        r = self.righe[self.k]; self.k += 1
        assert r["parola"] == parola, (r["parola"], parola)
        if r["n_osservazioni"] != len(osservazioni):
            self.stat["tabella_diversa"] += 1   # la risposta archiviata vide una tabella con meno righe
        dati = self.parser(r["risposta_raw"])
        self.stat["risposte"] += 1
        if dati is None:
            self.stat["senza_lista"] += 1
            return []
        cand = [c for c in (C.compila_candidato(x) for x in dati) if c is not None]
        self.stat["candidati_grezzi"] += len(dati)
        self.stat["compilati"] += len(cand)
        self.stat["coerenti"] += sum(1 for h in cand if all(
            h.vale(p, s) == pres for (p, s, pres) in osservazioni))
        return cand

def campagna(modello, parser, semi=30):
    prop = ProponenteReplay(modello, parser)
    esiti = {"NUR": collections.Counter(), "GUMO": collections.Counter()}
    canguri = 0
    for seed in range(semi):
        app = C.ApprendistaSeq(C.ParlanteSimSeq(C.verita_L2D), C.spazio_base(),
                               seed=seed, proponente=prop)
        app.fase_ostensione(); app.fase_probing(); app.fase_proposte()
        for w in ("NUR", "GUMO"):
            e = app.esito(w)
            esiti[w][e] += 1
        canguri += sum(1 for w in C.REGOLE_VERE if app.esito(w) == "CANGURO")
    return esiti, prop.stat, canguri

if __name__ == "__main__":
    for modello in ("claude-haiku-4-5", "claude-sonnet-4-6"):
        for nome, parser in (("parser v3", C._estrai_lista_json),
                             ("parser tollerante", parser_tollerante)):
            esiti, stat, k = campagna(modello, parser)
            print(f"{modello:18s} {nome:18s} NUR {esiti['NUR']['GIUSTA']:2d}/30  "
                  f"GUMO {esiti['GUMO']['GIUSTA']:2d}/30  canguri {k}  | "
                  f"risposte senza lista {stat['senza_lista']}/{stat['risposte']}, "
                  f"candidati compilati {stat['compilati']}/{stat['candidati_grezzi']}, "
                  f"coerenti col log {stat['coerenti']}/{stat['compilati']} "
                  f"({100*stat['coerenti']/max(1,stat['compilati']):.0f}%), "
                  f"tabella diversa {stat['tabella_diversa']}")
