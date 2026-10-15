# Protocol version v4 — revision of ARTL-2026-0189

This folder contains the code, results and figure sources of the revised
manuscript. It supersedes the `code/` folder of the archived preprint (protocol
version v3) for every simulated experiment. For the proposer experiment
(Section 5.3) the archived v3 raw responses are re-analysed offline, and the new
runs (a third proposer with the archived instrument; the three proposers with
the corrected v4 prompt) are included here with their raw responses.

## What changed from v3 (see Appendix C of the manuscript)

1. `orchestratore.py`: Eq. (2) is applied at **every** exchange to **every**
   anchor (`Orchestratore.CONDIVISIONE = True`; set it to `False` to reproduce
   the archived v3 behaviour). Anchors first heard after ostension receive their
   own minimal-pair pass. The recovery round constructs a targeted minimal pair
   for anchors lacking contrastive evidence before re-probing. A promoted anchor
   whose hypothesis set is emptied by later evidence is revoked. `metriche()`
   returns the class-aware outcomes of Eq. (6) (`giuste` = singleton correct,
   `sottodeterminate`, `canguri_residui` = truth excluded, `irrisolte`) plus
   `occam_errato` (how many underdetermined promotions the Occam choice would
   have got wrong).
2. `trappole.py`: the trap orchestrator ported to v4 (same pool logic; strong
   variant confined to the pool in minimal pairs, targeted pairs and probes).
   Reports "unresolved with the right referent" and the outcomes of all words.
3. `campagna.py`: CSV columns `sottodeterminate` and `occam_errato` added.
4. `condizioni.py`: unchanged learner (it already applied Eq. 2 at every
   exchange); a `ProponenteOpenAI` class was added so that a third proposer
   (`--modello gpt-4o-mini`) runs through the identical pipeline, and a
   `--prompt v4` option selects the corrected instrument, whose DSL examples
   match no rule of the lexicon (in v3 the `rel_n` and `or` examples were the
   true rules of NUR and GUMO). Output files carry the version suffix
   (`_v3` / `_v4`). `terzo_proponente_riassunto.py --modello M --versione V`
   summarizes a campaign (outcomes, parser statistics, copies of the prompt
   examples, lenient-parser replay).
5. New scripts: `mondo.py` (parametric world generator + v4 orchestrator;
   reproduces the base world exactly), `mondi_grandi.py`, `sweep_round.py`,
   `rumore2.py`, `campagna2.py` (v3 vs v4 side by side), `replay_proposer.py`
   (archived proposer responses replayed through the v3 and a lenient parser),
   `analisi_t2.py` (diagnosis of the 11 T2-weak outcomes under v3),
   `analisi_classi_v3.py`, `diag_v4.py`, `pilota_presupposizione.py`
   (reproduces the plurality-presupposition observation on the un-repaired
   prompt; 64 API calls), `harvest_v4.py` + `figures_v4.py` (all figures).

## Reproducing the tables and figures

All commands run from this folder (Python 3.10+, standard library only unless
noted). `replay_proposer.py` reads the archived proposer logs in
`../logs/proposer/` and `harvest_v4.py` the archived v3 results in
`../results/`, i.e. the preprint folders of this repository.

```bash
python campagna2.py 50                 # Table 3 (v4) and Table 11 (v3 vs v4)
python trappole.py                     # Table 5, trap T1 (zumu_forma)
python trappole.py --trappola tin_moto # Table 5, trap T2
python rumore2.py 50                   # Table 8
python mondi_grandi.py 50              # Tables 9-10 (all four worlds; ~2 min)
python sweep_round.py 50               # Figure 9 data (~5 min)
python replay_proposer.py              # parser replay of the archived v3 responses (Figure 7, shaded)
python condizioni.py --braccio base   --semi 30   # Table 6, base
python condizioni.py --braccio esteso --semi 30   # Table 6, oracle
python harvest_v4.py && python figures_v4.py      # data_v4.json + figs/Figure1-9
```

Proposer campaigns of Tables 6-7 (need API keys; their CSV results and raw
responses are archived in this folder, so the tables can be checked without
new calls):

```bash
export OPENAI_API_KEY=...; export ANTHROPIC_API_KEY=...
python condizioni.py --braccio llm --modello gpt-4o-mini --semi 30                   # third proposer, v3 instrument (87%)
python condizioni.py --braccio llm --prompt v4 --modello gpt-4o-mini --semi 30       # corrected instrument (47%)
python condizioni.py --braccio llm --prompt v4 --modello claude-haiku-4-5 --semi 30  # (15%)
python condizioni.py --braccio llm --prompt v4 --modello claude-sonnet-4-6 --semi 30 # (65%)
python terzo_proponente_riassunto.py --modello gpt-4o-mini --versione v4             # outcomes and Table 7 statistics of one campaign
```

Optional, need API keys (not used for the revised tables):

```bash
python campagna.py --llm --attiva --round2 --semi 10   # live check under v4
python pilota_presupposizione.py                        # plurality presupposition, 64 calls
```

## Result files

- `risultati_campagna2_v3_v4.csv` — base world, 4 conditions × 50 seeds, v3 and v4.
- `risultati_rumore2_v4.csv` — noise study, 6 levels × 50 seeds.
- `risultati_mondi_grandi_v4.csv` — four worlds × 4 conditions × 50 seeds.
- `risultati_sweep_round_v4.csv` — recovery-round sweep, four worlds.
- `risultati_replay_parser.txt` — parser replay summary.
- `risultati_condizioni_llm_gpt-4o-mini_v3.csv`, `proposte_raw_gpt-4o-mini_v3.jsonl` — third proposer, v3 instrument (60 calls, 24 Sep 2026).
- `risultati_condizioni_llm_<model>_v4.csv`, `proposte_raw_<model>_v4.jsonl` for the three models — corrected instrument (180 calls, 24 Sep 2026); `risultati_v4_riassunto.txt` — their summaries.
- `data_v4.json` — everything the figures use, produced by `harvest_v4.py`.
