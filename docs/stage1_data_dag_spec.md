# Stage 1 — Data and DAG specification  
## Transaction Enrichment Confidence

This document defines the **v1 variables, causal assumptions, and data-generating logic** for Stage 1.

It is the reference point for:
- the synthetic data generator, and
- the initial causal estimates.

Once finalized, this spec should not change without an explicit version bump.

---

## 1. Product question

If transaction enrichment confidence improves, how much would we expect downstream outcomes to change,
after accounting for realistic confounding?

We focus on:
- a **business outcome** (retention), and
- a **near-term mechanism** (edit rate) as an interpretable leading indicator.

---

## 2. Unit of analysis

Two linked units are used:

- **User–week**  
  Used for enrichment confidence and edit behavior.

- **User**  
  Used for week+4 retention, derived from the user’s prior weeks.

This structure allows us to model:
- confidence as something that varies over time and across users, and
- retention as a lagging outcome influenced by earlier experience.

---

## 3. Variables (v1)

### Treatment (T)

**`confidence`** (continuous, 0–1)  
Average transaction enrichment confidence for a given user in a given week.

Interpretation: how “clean” the transaction information appears to the user during that week.

---

### Outcomes (Y)

#### Leading / mechanism outcome

**`edit_rate`** (continuous, 0–1)  
Share of transactions edited by the user in a given week.

Edits include:
- merchant renaming,
- category changes,
- split or merge actions,
- notes added to correct transaction information.

Higher edit rates indicate greater friction and lower trust in automation.

---

#### Business outcome

**`wk4_retention`** (binary)  
Whether the user is active in week +4.

“Active” is intentionally abstract and may include:
- any app session,
- any transaction view,
- any meaningful interaction.

---

### Confounders (X)

These variables influence both confidence and outcomes.

- **`feed_quality`** (continuous, 0–1)  
  Captures data source reliability (bank/provider, region, connectivity).
  Affects confidence directly and also affects user experience and retention.

- **`txn_complexity`** (continuous, >0)  
  Captures how difficult a user’s transactions are to enrich:
  merchant diversity, cross-border activity, uncommon merchants, messy descriptors.
  Higher complexity reduces confidence and increases edits, and may relate to retention through user type.

- **`baseline_engagement`** (continuous, >0)  
  Captures underlying propensity to use the product.
  Strongly affects retention, influences edit behavior, and may correlate with observed confidence
  via learning or feedback effects.

Optional (explicitly excluded from v1 unless needed later):
- `country_or_region`
- `plan_tier`
- `tenure_weeks`

---

### Mediator (M)

- **`edit_rate`** lies on the path  
  `confidence → edit_rate → wk4_retention`

For Stage 1, we estimate the **total effect** of confidence on retention.

As a result:
- `edit_rate` is **not** controlled for when estimating `confidence → wk4_retention`.

Direct-effect or mediation analysis is explicitly out of scope for v1.

---

## 4. Causal assumptions (Stage 1)

We assume an *as-good-as-random* condition after adjustment:

> Conditional on observed confounders (`feed_quality`, `txn_complexity`, `baseline_engagement`),
> remaining variation in enrichment confidence is independent of potential outcomes.

This assumption is **not** claimed to hold automatically in real products.

In this repository, we:
- encode the assumption explicitly in a causal graph,
- generate synthetic data where it holds by construction,
- demonstrate failure modes (naive estimates, stronger confounding, feedback loops).

---

## 5. DAG (causal graph)

### Nodes

- Treatment: `confidence`
- Outcomes: `edit_rate`, `wk4_retention`
- Confounders: `feed_quality`, `txn_complexity`, `baseline_engagement`

---

### Edges

#### Confounding paths

- `feed_quality → confidence`
- `feed_quality → edit_rate`
- `feed_quality → wk4_retention`

- `txn_complexity → confidence`
- `txn_complexity → edit_rate`
- `txn_complexity → wk4_retention` (optional direct edge; see note below)

- `baseline_engagement → edit_rate`
- `baseline_engagement → wk4_retention`
- `baseline_engagement → confidence`  
  (used when modeling learning, feedback, or selection effects)

---

#### Core mechanism

- `confidence → edit_rate`
- `confidence → wk4_retention`
- `edit_rate → wk4_retention`

---

### Note on the `txn_complexity → wk4_retention` edge

This edge reflects realistic structure: transaction complexity can proxy for
business type, spending patterns, or financial maturity, which may influence
retention independently of enrichment quality.

It is included to avoid an unrealistically “clean” causal problem.

---

## 6. Estimands

### Estimand A — leading indicator

**Total effect of `confidence` on `edit_rate`.**

Interpretation:
> How much does improving enrichment confidence reduce user corrections?

---

### Estimand B — business outcome

**Total effect of `confidence` on `wk4_retention`.**

This effect:
- allows mediation through edit behavior,
- is expected to be smaller and noisier,
- is interpreted in conjunction with the edit-rate mechanism.

---

## 7. Identification plan

Using the DAG, we identify a valid backdoor adjustment set.

For both outcomes, we adjust for:
- `feed_quality`
- `txn_complexity`
- `baseline_engagement`

For retention:
- `edit_rate` is **not** included in the adjustment set,
  unless we explicitly switch to a direct-effect analysis in a later stage.

---

## 8. Synthetic data requirements

The data generator must ensure that:

- Naive correlations between confidence and retention are biased (typically overstated).
- After adjustment with a modern estimator, the ground-truth effect
  can be recovered in direction and approximate magnitude.
- Retention is lagging:
  - depends on earlier confidence and edit experience,
  - plus baseline engagement.

The generator should include:
- noise and measurement error in confidence,
- realistic distributions (confidence skewed high; edits sparse for some users),
- optional feedback loops:
  - edits improving future confidence through learning.

For v1, feedback may be included in a mild, transparent form.

---

## 9. Definition of done — Stage 1

Stage 1 is complete when the repository contains:

- This specification document
- A reproducible synthetic data generator consistent with this DAG
- A DoWhy setup that:
  - encodes the causal graph,
  - identifies the estimand,
  - runs at least two refutation tests
- One modern estimator (EconML or DoubleML) producing:
  - an estimate for `confidence → edit_rate`,
  - an estimate for `confidence → wk4_retention`
- A concise comparison of naive vs causal estimates with plain-language explanation
