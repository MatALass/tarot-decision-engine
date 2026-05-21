# Tarot Decision Engine

Moteur de décision Monte Carlo pour le **tarot français à 5 joueurs**.

Étant donné une main de 15 cartes, le moteur estime la probabilité de réussite
de chaque contrat par simulation, puis recommande le contrat optimal selon la
stratégie choisie.

---

## Installation

```bash
git clone <repo>
cd tarot-decision-engine
pip install -e ".[dev]"
```

Prérequis : Python ≥ 3.11.

---

## Usage CLI

### Commande principale

```
tarot-engine evaluate-hand [OPTIONS]
```

### Format des cartes

| Type    | Format          | Exemples                        |
|---------|-----------------|---------------------------------|
| Atout   | `T<n>`          | `T1`, `T10`, `T21`             |
| Excuse  | `EXCUSE`        | `EXCUSE`, `EXC`, `E`           |
| Couleur | `<rang><suit>`  | `KH`, `10D`, `AS`, `CD`        |

**Rangs :** `A`/`AS` · `2`–`10` · `V`/`J` (Valet) · `C` (Cavalier) · `D`/`Q` (Dame) · `K`/`R` (Roi)

**Couleurs :** `S` (Pique) · `H` (Cœur) · `D` (Carreau) · `C` (Trèfle)

---

## Exemples réalistes

### Évaluation basique — tous les contrats, politique conservative

```bash
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S"
```

### Politique expected_value — maximiser l'espérance de score

```bash
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --policy expected_value \
  --n-simulations 2000 \
  --seed 42
```

### Politique balanced — compromis rendement / risque

```bash
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --policy balanced \
  --risk-weight 1.0
```

`risk_weight` contrôle l'aversion au risque :
`utility = expected_score - risk_weight × score_std`.
Plus `risk_weight` est élevé, plus on pénalise la variance.

### Contrats ciblés uniquement

```bash
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --contracts PRISE \
  --contracts GARDE
```

### Sortie JSON pour scripting

```bash
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --output json \
  --seed 42
```

Exemple de sortie JSON :

```json
{
  "recommended_contract": "GARDE",
  "policy_name": "conservative",
  "rationale": "GARDE recommended by the conservative policy. Win rate: 71% over 200 simulations. Expected score: +176 pts (std: 303, range: -400 to +600). Alternatives: PRISE: lower expected score (+88 pts); ...",
  "warnings": [
    "Close call between GARDE and PRISE: the difference on the primary criterion is small."
  ],
  "contracts": [
    {
      "rank": 1,
      "contract": "GARDE",
      "win_rate": 0.71,
      "expected_score": 176.3,
      "score_std": 302.79,
      "score_min": -400,
      "score_max": 600,
      "score_q10": -288.4,
      "score_q50": 284.0,
      "score_q90": 473.2,
      "n_simulations": 200
    }
  ]
}
```

---

## Options complètes

```
tarot-engine evaluate-hand [OPTIONS]

Options:
  --hand, -h       TEXT                    15 cartes séparées par virgules  [required]
  --contracts, -c  TEXT                    Contrats à évaluer (répétable). Défaut: tous.
  --n-simulations  INT  [1<=x<=100000]     Simulations par contrat  [défaut: 1000]
  --seed           INT                     Graine aléatoire  [défaut: 0]
  --policy, -p     [conservative|          Politique de décision  [défaut: conservative]
                   expected_value|balanced]
  --risk-weight    FLOAT [x>=0.0]          Poids du risque pour la policy balanced  [défaut: 0.5]
  --output, -o     [text|json]             Format de sortie  [défaut: text]
  --help                                   Afficher l'aide
```

---

## Architecture

```
src/tarot_engine/
├── domain/           Modèle métier pur — aucune dépendance externe
│   ├── enums.py      Contract, Suit, Rank, PlayerRole, BidAction
│   ├── cards.py      Card (frozen dataclass, factories, point_value, is_bout)
│   ├── deck.py       generate_deck(), validate_deck()
│   ├── hand.py       Hand, Dog (immutables, validés à la construction)
│   ├── rules.py      legal_cards(), trick_winner(), SuitLead/TrumpLead
│   └── scoring.py    required_points(), score_deal(), DealResult
│
├── simulation/       Monte Carlo — dépend uniquement de domain/
│   ├── sampler.py    sample_deal() — distribution des mains inconnues
│   ├── policies.py   choose_card() — heuristique de jeu (déterministe)
│   ├── game_runner.py  run_deal() — exécution d'une donne complète
│   └── monte_carlo.py  simulate_contract() — boucle N simulations
│
├── decision/         Évaluation et recommandation — ne simule pas
│   ├── models.py     ContractEvaluation, RankedContract, DecisionRecommendation
│   ├── evaluator.py  evaluate_contract(), evaluate_contracts()
│   ├── policies.py   ConservativePolicy, ExpectedValuePolicy, BalancedPolicy
│   └── explainer.py  explain() — rationale textuelle factuelle
│
├── application/      Câblage frontière externe — Pydantic pour la validation
│   ├── dto.py        EvaluationRequest, EvaluationResponse
│   └── services.py   evaluate_hand() — orchestration complète
│
├── cli/              Interface utilisateur
│   └── main.py       Typer app, evaluate-hand subcommand, rendu texte/JSON
│
└── utils/
    ├── parsing.py    str → Card (syntaxique uniquement, sans logique métier)
    └── random.py     make_rng(seed) — RNG seeded centralisé
```

**Invariant de dépendance strict :**

```
domain ← simulation ← decision ← application ← cli
```

Aucune couche ne dépend d'une couche supérieure. `domain` n'importe rien du projet.

---

## Reproductibilité

Toute simulation est entièrement reproductible via `--seed`.

- `make_rng(seed)` crée un `random.Random` isolé — pas de global state.
- La simulation *i* utilise la graine `seed + i`, indépendamment du nombre total de simulations.
- Ajouter des simulations ne modifie jamais les résultats des simulations précédentes.

```bash
# Ces deux commandes produisent exactement les mêmes 100 premiers scores
tarot-engine evaluate-hand --hand "..." --n-simulations 100 --seed 0
tarot-engine evaluate-hand --hand "..." --n-simulations 500 --seed 0
```

---

## Tests et qualité

```bash
# Lancer tous les tests
python -m pytest tests/ -q

# Avec couverture
python -m pytest tests/ --cov=tarot_engine --cov-report=term-missing

# Lint
ruff check src/ tests/

# Format check
ruff format --check src/ tests/
```

**155 tests** — unitaires + intégration + CLI.

---

## Hypothèses et limites du MVP

### Règles implémentées

- Composition correcte : 78 cartes (56 couleur + 21 atouts + Excuse).
- Distribution à 5 joueurs : 15 cartes par joueur, 3 au chien.
- Contrats : Prise (×1), Garde (×2), Garde sans (×4), Garde contre (×6).
- Légalité des coups : suivre couleur → couper (avec surcoupage obligatoire) → défausser.
- Résolution du pli : atout le plus fort > couleur demandée la plus forte; l'Excuse ne gagne jamais.
- Scoring : seuils par nombre de bouts (56/51/41/36), bonus de contrat 25 pts, distribution sur 4 joueurs.
- Échange avec le chien (Prise/Garde) : le preneur prend les 3 cartes, écarte 3 non-bouts non-rois en priorité.

### Simplifications assumées

| Sujet | Simplification MVP |
|---|---|
| Politique de jeu | Une seule heuristique pour tous les joueurs (pas de stratégie taker/défenseur différenciée) |
| Appel du roi | Heuristique : préférer le roi d'une couleur absente de la main du preneur |
| Protection partenaire | Non implémentée dans `legal_cards()` — paramètre `partner_player_index` réservé |
| Excuse | Ne gagne jamais un pli ; pas d'échange de fin de partie |
| Primes et annonces | Poignée, Petit au bout, Chelem non implémentés |

### Ce qui n'est pas dans le MVP

- Analyse de coups en cours de partie (mid-game).
- Inférence sur les mains adverses à partir des cartes jouées.
- Interface web ou API REST.
- Apprentissage automatique.

---

## Scénario de démonstration recommandé

```bash
# 1. Main forte (3 bouts + 8 atouts) — doit recommander Garde ou plus
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --n-simulations 500 --seed 42

# 2. Main faible (0 bout, 2 atouts) — win rates bas sur tous les contrats
tarot-engine evaluate-hand \
  --hand "2H,3H,4H,5H,6H,2S,3S,4S,5S,6S,2D,3D,T5,T6,7H" \
  --n-simulations 500 --seed 42

# 3. Comparer les trois politiques sur la même main (JSON)
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --policy conservative --n-simulations 500 --seed 42 --output json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('conservative ->', d['recommended_contract'])"

tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --policy expected_value --n-simulations 500 --seed 42 --output json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('expected_value ->', d['recommended_contract'])"

tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --policy balanced --risk-weight 0.5 --n-simulations 500 --seed 42 --output json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('balanced    ->', d['recommended_contract'])"

# 4. Export JSON pour intégration
tarot-engine evaluate-hand \
  --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S" \
  --output json --seed 42 > result.json && echo "Saved to result.json"
```
