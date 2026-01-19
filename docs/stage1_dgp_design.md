# Stage 1 — Synthetic DGP Design

## Transaction Enrichment Confidence

This document specifies the synthetic data-generating process (DGP) used in Stage 1.

The DGP is designed to be:

- realistic enough to reproduce the same failure modes as real product data,
- explicit enough that ground-truth causal effects are known,
- stable enough to reproduce results across runs.

The goal is **not** to simulate reality.

The goal is to create a controlled environment where causal reasoning is required, testable, and inspectable.

---

## 1. High-level structure
We simulate users over multiple weeks.
Each user has stable traits:

- baseline engagement tendency,
- transaction complexity,
- feed quality (data source reliability).

Each week:
- the system produces an enrichment confidence score,
- users experience friction, measured as edit rate.

Retention at week +4 depends on:
- earlier confidence and edit experience,
- baseline engagement,
- feed quality and transaction complexity.

Confounding is intentionally baked in so that naive correlations are biased.

---

## 2. Indices and timeline
- Users: `i = 1..N`
- Weeks: `t = 1..T` (for v1, `T = 8`)

Outcomes:
-  `confidence_{i,t}`, `edit_rate_{i,t}` at the user–week level
-  `wk4_retention_i` at the user level

To keep the setup simple and interpretable:
- define an index week `t0 = 1`,
- define retention as activity in week `t0 + 4`,
- use weeks 1–4 as the exposure window influencing retention.

Rolling or repeated retention is explicitly out of scope for v1.

---

## 3. Latent user traits (confounders)

Each user is assigned three latent traits.

### Baseline engagement (stickiness)

`E_i ~ LogNormal(μ_E, σ_E)`

Interpretation:
- higher values indicate stronger underlying usage propensity,
- strongly affects retention,
- increases observed edit behavior via greater usage,
- may correlate with confidence through learning or feedback effects.

---

### Transaction complexity

`C_i ~ LogNormal(μ_C, σ_C)`

Interpretation:
- higher values represent harder-to-enrich transaction streams,
- lowers confidence,
- increases edits,
- may influence retention independently of enrichment quality.

---

### Feed quality

`F_i ~ Beta(a_F, b_F)`

Interpretation:
- captures data source reliability (bank, region, connectivity),
- directly improves confidence,
- improves user experience and retention independently.

---

For modeling convenience, all three variables are standardized:
-  `E*_i`, `C*_i`, `F*_i` (mean 0, standard deviation 1)

---

## 4. Weekly transaction volume (optional)

To make edit rates meaningful, we optionally simulate transaction counts:

`n_txn_{i,t} ~ Poisson(λ_i)`

with

`log λ_i = α_n + β_nE · E*_i`

More engaged users see more transactions and therefore more opportunities to edit.

This component is useful but not strictly required for v1.

---

## 5. Treatment: enrichment confidence (user–week)

Enrichment confidence should:
- increase with feed quality,
- decrease with transaction complexity,
- increase slightly with engagement (optional),
- vary week to week,
- be skewed toward higher values for many users.

We model a latent score and map it to (0, 1).

Latent confidence:

```css
conf_latent_{i,t} =
α_c
b_F · F*_i
b_C · C*_i
b_E · E*_i
u_{i,t}
```
where
`u_{i,t} ~ Normal(0, σ_c_week)`

Observed confidence:
```yaml
confidence_{i,t} = sigmoid(conf_latent_{i,t})
```

Key properties:
- confidence is caused by confounders, not random,
- week-level noise introduces realistic instability,
- distributions resemble real quality metrics.

---

## 6. Mechanism outcome: edit rate (user–week)

Edit rate should:
- decrease as confidence increases (causal effect of interest),
- increase with transaction complexity,
- increase with engagement,
- be bounded in [0, 1],
- be low for many users.

Latent edit propensity:
```css
edit_latent_{i,t} =
α_e
τ_e · confidence_{i,t}
g_C · C*_i
g_E · E*_i
g_F · F*_i
ε_{i,t}
```
where
`ε_{i,t} ~ Normal(0, σ_e)`

Observed edit rate:
```yaml
edit_rate_{i,t} = sigmoid(edit_latent_{i,t})
```
Ground-truth causal effect:
-  `τ_e` controls the strength of `confidence → edit_rate`.

Confounding is aligned so that naive estimates are biased:
- feed quality improves confidence and reduces edits,
- complexity reduces confidence and increases edits.

---

## 7. Business outcome: week+4 retention (user-level)

Retention is a lagging outcome.

It depends on:
- baseline engagement (strongly),
- feed quality directly,
- transaction complexity,
- cumulative experience over weeks 1–4.

Define exposure summaries:
-  `conf_mean_i = mean(confidence_{i,t})`, `t = 1..4`
-  `edit_mean_i = mean(edit_rate_{i,t})`, `t = 1..4`

Latent retention log-odds:

```css
ret_latent_i =
α_r
δ_E · E*_i
δ_F · F*_i
δ_C · C*_i
τ_r · conf_mean_i
κ_r · edit_mean_i
ν_i
```
where
`ν_i ~ Normal(0, σ_r)`

Observed retention:
```yaml
wk4_retention_i ~ Bernoulli(sigmoid(ret_latent_i))
```

Ground-truth causal pathways:
- direct effect: `confidence → retention` (`τ_r`),
- mediated effect: `confidence → edit_rate → retention` (`τ_e`, `κ_r`).

Stage 1 estimands treat retention effects as **total effects**.

---

## 8. Optional feedback loop (advanced)

Real systems often learn from corrections:
- higher edit rates can improve future confidence.

We optionally introduce:
```yaml
conf_latent_{i,t+1} += ω · edit_rate_{i,t}
```

This creates time-dependent confounding.

For Stage 1:
- default is `ω = 0`,
-  `ω > 0` may be introduced later as a stress test.

This behavior must be explicit and documented when enabled.

---

## 9. Parameter defaults (starter values)

These values are intended to produce sensible behavior, not realism.

**Confidence model**

-  `α_c = 1.0`
-  `b_F = 1.2`
-  `b_C = 1.0`
-  `b_E = 0.2`
-  `σ_c_week = 0.6`

**Edit model**

-  `α_e = -1.8`
-  `τ_e = 2.0`
-  `g_C = 0.8`
-  `g_E = 0.4`
-  `g_F = 0.3`
-  `σ_e = 0.5`

**Retention model**

-  `α_r = -0.3`
-  `δ_E = 1.4`
-  `δ_F = 0.4`
-  `δ_C = 0.1`
-  `τ_r = 0.8`
-  `κ_r = 1.0`
-  `σ_r = 0.4`

Tuning guidance:
- reduce `α_r` if retention is too high,
- increase `τ_r` or `τ_e` if confidence effects are too weak,
- increase `b_F`, `b_C`, `g_C`, `g_F` to amplify naive bias.

---

## 10. Ground truth tracking

We explicitly record:
-  `τ_e` (confidence → edit_rate),
-  `τ_r` and the implied total effect on retention.

Estimators are evaluated by comparing:
- naive correlations vs ground truth,
- adjusted causal estimates vs ground truth,
- behavior under stronger or weaker confounding.

---

## 11. Required outputs from the generator

At minimum, the generator must produce:

**User-level table**
-  `user_id`
-  `E`, `C`, `F` (and standardized versions)
-  `wk4_retention`

**User–week table**
-  `user_id`
-  `week`
-  `confidence`
-  `edit_rate`
- optional: `n_txn`

Wide or convenience views may be added as needed.

---

## 12. Definition of done

This DGP is considered complete when:
- confidence distributions are mostly high and plausible,
- edit rates are mostly low with realistic spread,
- naive analysis is visibly biased,
- causal methods can recover ground truth under the stated adjustment set.