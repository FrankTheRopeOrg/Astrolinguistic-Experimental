"""
Micro-mondo parametrico e protocollo anti-canguro (versione v4)
================================================================
Generalizza orchestratore.py a un mondo con un numero arbitrario di attributi
e di valori per attributo, mantenendo IDENTICI il protocollo, i criteri di
selezione attiva e l'uso dei generatori casuali: con la specifica del mondo
originale (forma/colore/moto binari, n = 1..4) riproduce esattamente i
risultati di orchestratore.py (v4).

Lessico L2 ("alieno"), per costruzione trasversale a L1:
  - una parola FUSA per ogni coppia (colore, moto)          [congiunzioni]
  - una parola di PARITA' del numero (TAK pari / TIN dispari)
  - la forma NON e' codificata (dimensione assente)
  - ogni attributo aggiuntivo (es. taglia) e' codificato atomicamente

Protocollo v4:
  - Eq. (2) applicata a OGNI scambio e a TUTTE le ancore
  - ostensione (6 scene casuali) -> coppie minime (base casuale, per ogni
    ancora, comprese quelle udite dopo l'ostensione) -> M=3 probe
    pre-registrati (casuali o attivi) -> promozione (round pulito + >=1
    coppia discriminante)
  - round di recupero (opzionale): per le ancore non promosse, UNA coppia
    minima mirata se manca l'evidenza contrastiva, poi M probe con criterio
    piu' severo (>=1 probe positivo); revoca (quarantena) di una promossa
    che fallisce un probe o il cui insieme di ipotesi si svuota
  - budget opzionale di scambi (troncamento a parita' di costo)
"""
import itertools
import json
import random
import time


class Scena:
    __slots__ = ("val", "n", "_attr")

    def __init__(self, val: tuple, n: int, nomi: tuple):
        self.val = val
        self.n = n
        d = dict(zip(nomi, val))
        d["parita"] = "pari" if n % 2 == 0 else "dispari"
        self._attr = d

    def attributi(self) -> dict:
        return self._attr

    def __eq__(self, o):
        return self.val == o.val and self.n == o.n

    def __hash__(self):
        return hash((self.val, self.n))

    def __lt__(self, o):
        return (self.val, self.n) < (o.val, o.n)

    def __repr__(self):
        return f"Scena{self.val + (self.n,)}"


def _vale(ipotesi, scena) -> bool:
    attr = scena.attributi()
    return all(attr[k] == v for (k, v) in ipotesi)


class Mondo:
    def __init__(self, attributi: dict, n_max: int = 4,
                 fusione=("colore", "moto"), assente="forma"):
        self.attributi = dict(attributi)           # nome -> lista valori
        self.nomi = tuple(self.attributi)
        self.n_max = n_max
        self.fusione = fusione
        self.assente = assente
        self.scene = [Scena(v, n, self.nomi) for v, n in itertools.product(
            itertools.product(*self.attributi.values()), range(1, n_max + 1))]
        self.atomi = {(k, v) for k, vals in self.attributi.items() for v in vals} | \
                     {("parita", "pari"), ("parita", "dispari")}
        self.ipotesi_universo = {frozenset([a]) for a in self.atomi} | \
            {frozenset([a, b]) for a in self.atomi for b in self.atomi
             if a < b and a[0] != b[0]}
        # --- lessico L2 ---
        self.referenti = {}
        fa, fb = fusione
        self.parola_fusa = {}
        for i, (va, vb) in enumerate(itertools.product(
                self.attributi[fa], self.attributi[fb])):
            w = f"Z{i:02d}"
            self.parola_fusa[(va, vb)] = w
            self.referenti[w] = frozenset({(fa, va), (fb, vb)})
        self.referenti["TAK"] = frozenset({("parita", "pari")})
        self.referenti["TIN"] = frozenset({("parita", "dispari")})
        self.parola_atomica = {}
        for k in self.nomi:
            if k in fusione or k == assente:
                continue
            for j, v in enumerate(self.attributi[k]):
                w = f"{k[0].upper()}{j:02d}"
                self.parola_atomica[(k, v)] = w
                self.referenti[w] = frozenset({(k, v)})
        # nomi leggibili per il mondo originale
        if self.attributi == {"forma": ["triangolo", "cerchio"],
                              "colore": ["rosso", "blu"],
                              "moto": ["rapido", "fermo"]}:
            ren = {"Z00": "ZUMU", "Z01": "ZAKA", "Z02": "ZIBO", "Z03": "ZEFU"}
            self.referenti = {ren.get(w, w): r for w, r in self.referenti.items()}
            self.parola_fusa = {k: ren.get(w, w) for k, w in self.parola_fusa.items()}

    def verita_L2(self, s: Scena) -> str:
        a = s.attributi()
        fa, fb = self.fusione
        parole = [self.parola_fusa[(a[fa], a[fb])],
                  "TAK" if s.n % 2 == 0 else "TIN"]
        for (k, v), w in sorted(self.parola_atomica.items()):
            if a[k] == v:
                parole.append(w)
        return " ".join(parole)

    def coppia_minima(self, s: Scena, attributo: str) -> Scena:
        if attributo == "parita":
            n = s.n + 1 if s.n < self.n_max else s.n - 1
            return Scena(s.val, n, self.nomi)
        i = self.nomi.index(attributo)
        vals = self.attributi[attributo]
        nuovo = vals[(vals.index(s.val[i]) + 1) % len(vals)]   # binario: l'altro
        val = s.val[:i] + (nuovo,) + s.val[i + 1:]
        return Scena(val, s.n, self.nomi)


MONDO_ORIGINALE = dict(attributi={"forma": ["triangolo", "cerchio"],
                                  "colore": ["rosso", "blu"],
                                  "moto": ["rapido", "fermo"]}, n_max=4)


class ParlanteSim:
    def __init__(self, mondo: Mondo):
        self.mondo = mondo
    def etichetta(self, s):
        return self.mondo.verita_L2(s)


class ParlanteRumoroso(ParlanteSim):
    """Inverte la presenza di ogni parola L2 con probabilita' p (RNG dedicato)."""
    def __init__(self, mondo, p, seed):
        super().__init__(mondo)
        self.p = p
        self.rng = random.Random(10_000 + seed)
        self.vocab = sorted(mondo.referenti)
    def etichetta(self, s):
        parole = set(self.mondo.verita_L2(s).split())
        for w in self.vocab:
            if self.rng.random() < self.p:
                parole.symmetric_difference_update({w})
        return " ".join(sorted(parole))


class BudgetEsaurito(Exception):
    pass


class Ancora:
    def __init__(self, parola, universo):
        self.parola = parola
        self.stato = "PROVVISORIA"
        self.ipotesi = set(universo)
        self.coppie_discriminanti = 0
        self.probe_ok = 0
        self.probe_falliti = 0
        self.round_promozione = None
        self.scene_probe = []
        self.coppie_fatte = False

    def osserva(self, scena, presente):
        self.ipotesi = {h for h in self.ipotesi if _vale(h, scena) == presente}

    def referente_stimato(self):
        if not self.ipotesi:
            return set()
        canoniche = sorted(self.ipotesi, key=lambda h: (len(h), sorted(h)))
        return set(canoniche[0])


class OrchestratoreG:
    M_PROBE = 3

    def __init__(self, mondo: Mondo, parlante, seed=0, attiva=False,
                 budget=None, coppie_per_tutte=True, logfile=None):
        self.m = mondo
        self.p2 = parlante
        self.rng = random.Random(seed)
        self.attiva = attiva
        self.budget = budget
        self.coppie_per_tutte = coppie_per_tutte
        self.ancore = {}
        self.scambi = 0
        self.log = open(logfile, "w", encoding="utf-8") if logfile else None
        # contatori di costo computazionale
        self.valutazioni = 0      # valutazioni ipotesi-su-scena (Eq. 2 + argmax)
        self.t0 = time.perf_counter()

    # ---------------- evidenza -----------------------------------------
    def _osserva_tutte(self, scena, parole):
        for w, a in sorted(self.ancore.items()):
            if a.stato == "REVOCATA":
                continue
            self.valutazioni += len(a.ipotesi)
            a.osserva(scena, presente=(w in parole))
            if a.stato == "PROMOSSA" and not a.ipotesi:
                a.stato = "REVOCATA"

    def _chiedi(self, scena):
        if self.budget is not None and self.scambi >= self.budget:
            raise BudgetEsaurito()
        self.scambi += 1
        risposta = self.p2.etichetta(scena)
        parole = set(risposta.split())
        for w in sorted(parole):
            self.ancore.setdefault(w, Ancora(w, self.m.ipotesi_universo))
        if self.log:
            self.log.write(json.dumps({"scambio": self.scambi,
                                       "scena": scena.val + (scena.n,),
                                       "risposta_L2": risposta}) + "\n")
        self._osserva_tutte(scena, parole)
        return parole

    # ---------------- selezione attiva ---------------------------------
    def _scena_probe(self, a, gia_usate, candidati=None):
        H = sorted(a.ipotesi, key=lambda h: sorted(h))
        visti = {}
        for s_prec in gia_usate:
            for k, v in s_prec.attributi().items():
                visti.setdefault(k, set()).add(v)
        migliore, chiave_migliore = None, None
        usate = set(gia_usate)
        for s in (candidati or self.m.scene):
            if s in usate:
                continue
            self.valutazioni += len(H)
            voti = sum(1 for h in H if _vale(h, s))
            split = min(voti, len(H) - voti)
            attesa_presente = 1 if voti > 0 else 0
            novita = sum(1 for k, v in s.attributi().items()
                         if v not in visti.get(k, set()))
            chiave = (split, attesa_presente, novita)
            if chiave_migliore is None or chiave > chiave_migliore:
                migliore, chiave_migliore = s, chiave
        return migliore if migliore is not None else self.rng.choice(self.m.scene)

    # ---------------- fasi ---------------------------------------------
    def fase_ostensione(self, n_scene=6):
        for s in self.rng.sample(self.m.scene, n_scene):
            self._chiedi(s)

    def _coppie_di(self, a, base_fn):
        attributi_da_testare = {k for h in a.ipotesi for (k, v) in h}
        for attr in sorted(attributi_da_testare):
            base = base_fn(a, attr)
            if base is None:
                continue
            variata = self.m.coppia_minima(base, attr)
            w_base = a.parola in self._chiedi(base)
            w_var = a.parola in self._chiedi(variata)
            if w_base != w_var:
                a.coppie_discriminanti += 1
        a.coppie_fatte = True

    def fase_coppie_minime(self):
        base_casuale = lambda a, attr: self.rng.choice(self.m.scene)
        for a in sorted(self.ancore.values(), key=lambda x: x.parola):
            self._coppie_di(a, base_casuale)
        if self.coppie_per_tutte:      # ancore udite per la prima volta durante la fase
            while True:
                restanti = [a for a in sorted(self.ancore.values(), key=lambda x: x.parola)
                            if not a.coppie_fatte]
                if not restanti:
                    break
                for a in restanti:
                    self._coppie_di(a, base_casuale)

    def _base_mirata(self, a, attr):
        """Coppia minima MIRATA (round di recupero): scena su cui le ipotesi
        superstiti predicono la parola PRESENTE e che contiene l'attributo."""
        for s in self.m.scene:
            if any(_vale(h, s) for h in a.ipotesi):
                return s
        return None

    def fase_probing(self, round_n=1, mirata=False):
        for a in sorted(self.ancore.values(), key=lambda x: x.parola):
            if a.stato in ("PROMOSSA", "REVOCATA") or len(a.ipotesi) == 0:
                continue
            if mirata and a.coppie_discriminanti == 0:
                self._coppie_di(a, self._base_mirata)
                if len(a.ipotesi) == 0:
                    continue
            ok_round, falliti_round, positivi_round = 0, 0, 0
            for _ in range(self.M_PROBE):
                if self.attiva:
                    s = self._scena_probe(a, a.scene_probe)
                else:
                    s = self.rng.choice(self.m.scene)
                a.scene_probe.append(s)
                predizione = any(_vale(h, s) for h in a.ipotesi)
                parole = self._chiedi(s)          # aggiorna tutte le ancore
                reale = a.parola in parole
                if predizione == reale:
                    ok_round += 1
                    a.probe_ok += 1
                    if reale:
                        positivi_round += 1
                else:
                    falliti_round += 1
                    a.probe_falliti += 1
            promuovi = (ok_round >= self.M_PROBE and falliti_round == 0
                        and a.coppie_discriminanti >= 1)
            if round_n >= 2:
                promuovi = promuovi and positivi_round >= 1
            if promuovi:
                a.stato = "PROMOSSA"
                a.round_promozione = round_n
            elif falliti_round > 0:
                a.stato = "REVOCATA" if a.stato == "PROMOSSA" else "IRRISOLTA"

    def esegui(self, round2=False, n_ostensione=6, round_max=None):
        """Protocollo completo; il budget tronca la sequenza senza eccezioni.
        round_max: numero totale di round di probing (round2=True equivale
        a round_max=2); i round >= 2 sono round di recupero."""
        if round_max is None:
            round_max = 2 if round2 else 1
        try:
            self.fase_ostensione(n_ostensione)
            self.fase_coppie_minime()
            self.fase_probing(round_n=1)
            for r in range(2, round_max + 1):
                self.fase_probing(round_n=r, mirata=True)
        except BudgetEsaurito:
            pass
        if self.log:
            self.log.close()
        return self.metriche()

    # ---------------- esiti --------------------------------------------
    def metriche(self):
        out = {"giuste": 0, "sottodeterminate": 0, "occam_errato": 0,
               "canguri": 0, "irrisolte": 0, "irrisolte_giuste": 0,
               "revocate": 0, "scambi": self.scambi,
               "rec_r2": 0, "valutazioni": self.valutazioni,
               "secondi": time.perf_counter() - self.t0,
               "parole_udite": len(self.ancore), "parole_lessico": len(self.m.referenti)}
        for w, a in sorted(self.ancore.items()):
            vero = self.m.referenti[w]
            sup = {frozenset(h) for h in a.ipotesi}
            if a.stato == "REVOCATA":
                out["revocate"] += 1
                out["irrisolte"] += 1
            elif a.stato != "PROMOSSA" or not sup:
                out["irrisolte"] += 1
                if sup == {vero}:
                    out["irrisolte_giuste"] += 1
            elif vero not in sup:
                out["canguri"] += 1
            elif len(sup) == 1:
                out["giuste"] += 1
            else:
                out["sottodeterminate"] += 1
                if frozenset(a.referente_stimato()) != vero:
                    out["occam_errato"] += 1
            if a.round_promozione is not None and a.round_promozione >= 2:
                out["rec_r2"] += 1
        # parole del lessico mai udite: irrisolte per definizione
        mai = len(self.m.referenti) - len(self.ancore)
        out["irrisolte"] += mai
        out["mai_udite"] = mai
        return out


def run(mondo, seed, attiva, round2, budget=None, p_rumore=0.0,
        coppie_per_tutte=True, n_ostensione=6, round_max=None):
    parlante = ParlanteSim(mondo) if p_rumore == 0 else ParlanteRumoroso(mondo, p_rumore, seed)
    o = OrchestratoreG(mondo, parlante, seed=seed, attiva=attiva, budget=budget,
                       coppie_per_tutte=coppie_per_tutte)
    return o.esegui(round2=round2, n_ostensione=n_ostensione, round_max=round_max)


if __name__ == "__main__":
    import statistics
    m = Mondo(**MONDO_ORIGINALE)
    print(f"mondo originale: {len(m.scene)} scene, {len(m.ipotesi_universo)} ipotesi, "
          f"{len(m.referenti)} parole L2")
    for cpt in (False, True):
        print(f"\n-- coppie minime per tutte le ancore = {cpt} --")
        for nome, att, r2 in [("Random", False, False), ("Random+R2", False, True),
                              ("Active", True, False), ("Active+R2", True, True)]:
            R = [run(m, s, att, r2, coppie_per_tutte=cpt) for s in range(50)]
            def ms(k):
                v = [r[k] for r in R]
                return f"{statistics.mean(v):.2f}±{statistics.stdev(v):.2f}"
            print(f"{nome:10s} giuste {ms('giuste')} sottod {ms('sottodeterminate')} "
                  f"canguri {ms('canguri')} irrisolte {ms('irrisolte')} "
                  f"(di cui giuste {sum(r['irrisolte_giuste'] for r in R)}) "
                  f"scambi {ms('scambi')} recR2 {sum(r['rec_r2'] for r in R)}")
