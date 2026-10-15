"""
Pilota: presupposizione di pluralita' e raddoppio per oggetto (revisione, punto 2)
==================================================================================
Interroga GPT-4o-mini su TUTTE le 32 scene con (a) il prompt L2 ORIGINALE del
demo (hello_world.py, senza le due frasi di riparazione) e (b) il prompt L2
FINALE (orchestratore.py), e misura per ciascuno la fedelta' di esecuzione,
separando le scene con un solo oggetto dalle altre. 64 chiamate, costo di
centesimi. Richiede OPENAI_API_KEY.

Uso: python pilota_presupposizione.py
"""
import json
import os
from collections import Counter

from orchestratore import TUTTE_LE_SCENE, verita_L2, LESSICO_L2_PROMPT
from hello_world import LESSICO_L2 as LESSICO_L2_ORIGINALE

def chiedi(client, prompt, scena):
    r = client.chat.completions.create(
        model="gpt-4o-mini", max_tokens=30, temperature=0,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": scena.testo()}])
    return r.choices[0].message.content.strip()

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Errore: OPENAI_API_KEY non impostata.")
    import openai
    client = openai.OpenAI()
    out = open("pilota_presupposizione.jsonl", "w", encoding="utf-8")
    for nome, prompt in (("originale", LESSICO_L2_ORIGINALE), ("finale", LESSICO_L2_PROMPT)):
        fedeli = Counter(); tot = Counter(); errori = []
        for s in TUTTE_LE_SCENE:
            risp = chiedi(client, prompt, s)
            atteso = set(verita_L2(s).split())
            parole = risp.split()
            gruppo = "n=1" if s.n == 1 else "n>1"
            tot[gruppo] += 1
            ok = set(parole) == atteso and len(parole) == len(atteso)
            fedeli[gruppo] += ok
            if not ok:
                errori.append((s.testo(), risp, " ".join(sorted(atteso))))
            out.write(json.dumps({"prompt": nome, "scena": s.testo(), "risposta": risp,
                                  "atteso": verita_L2(s), "fedele": ok}) + "\n")
        print(f"\n=== prompt {nome} ===")
        for g in ("n=1", "n>1"):
            print(f"  scene {g}: fedeli {fedeli[g]}/{tot[g]}")
        for e in errori:
            print("  ERRORE:", e[0], "->", e[1], "| atteso:", e[2])
    out.close()
    print("\nLog: pilota_presupposizione.jsonl")
