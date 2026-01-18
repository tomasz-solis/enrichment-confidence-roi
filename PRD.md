# PRD — Transaction Enrichment Confidence  
## From Causal Impact to Decision Framing

---

## 1. Background and motivation

Many fintech products rely on transaction enrichment (merchant normalization, categorization, counterparty detection) to power user-facing features and automation.

Enrichment quality is often summarized as a confidence score, and teams invest heavily in improving it. In practice, however:

- Confidence is not randomly distributed.
- Improvements become increasingly expensive at higher levels.
- Downstream product impact often flattens well before “perfect” quality is reached.

This project exists to help product teams reason clearly about:
- whether improving enrichment confidence *causally* affects downstream outcomes, and
- how to recognize when further optimization is likely to face diminishing returns.

The project is intentionally abstracted and uses synthetic data.  
It does **not** model any real company’s system.

---

## 2. Problem statement

Product teams frequently ask:

- Should we invest more in improving enrichment quality?
- Is the current confidence level already good enough?
- Are we chasing the last 1–2% with little user or business impact?

These questions cannot be answered with simple correlations. Enrichment confidence is strongly confounded with:

- transaction complexity,
- data source quality,
- user behavior and engagement,
- geography and merchant mix.

This PRD defines a structured approach to answering these questions by using **causal inference as an input** and **decision framing as an output**.

---

## 3. Goals

### Primary goals

- Estimate the causal impact of transaction enrichment confidence on downstream product outcomes.
- Understand how this impact varies across the confidence range (non-linearity).
- Provide a clear framework for identifying diminishing returns without declaring a single “correct” KPI target.

### Secondary goals

- Apply modern causal inference tooling in a controlled setting.
- Demonstrate how causal analysis feeds into product decision-making.
- Produce artifacts that are readable by Product Managers, not only data scientists.

---

## 4. Explicit non-goals

This project does **not** aim to:

- define the “right” confidence threshold for a real product,
- optimize a production model,
- claim externally valid numeric results,
- replicate any internal system or workflow,
- provide definitive ROI estimates.

All numeric outputs are illustrative, not prescriptive.

---

## 5. Key concepts and definitions

### Transaction enrichment confidence

A continuous score `c ∈ [0, 1]` representing the system’s confidence that a transaction has been enriched correctly.

Conceptual examples include:
- merchant name normalization,
- category assignment,
- counterparty identification.

### Downstream outcomes

A small, focused set of user- or product-level signals, such as:
- transaction edit rate,
- feature engagement,
- short-term retention,
- support contact proxy.

---

## 6. Users and stakeholders

### Primary audience

- Product Managers working on data-heavy fintech features
- Product Data Scientists and Analysts

### Secondary audience

- ML engineers interested in downstream value
- Hiring managers evaluating decision-science capability

---

## 7. Approach overview

The project is structured in three stages, each building on the previous one.

---

### Stage 1 — Causal foundation

**Question**  
What is the causal effect of enrichment confidence on downstream outcomes?

**Approach**
- Define a causal graph with realistic confounding.
- Generate synthetic data from a known data-generating process.
- Compare naive correlations to causal estimates.
- Use DoWhy for identification and refutation.
- Use EconML / DoubleML for estimation.

**Outputs**
- Causal effect estimates with assumptions made explicit.
- Demonstration of bias in naive approaches.

---

### Stage 2 — Response curve and heterogeneity

**Question**  
How does the effect change across the confidence range?

**Approach**
- Treat confidence as a continuous treatment.
- Estimate dose–response curves.
- Inspect marginal effects and diminishing returns.
- Optionally slice by simple segments (e.g. transaction complexity).

**Outputs**
- Response curve visualizations.
- Marginal impact plots.
- Clear articulation of where effects flatten.

---

### Stage 3 — Decision framing (not prescription)

**Question**  
How might a product team reason about “good enough” quality?

**Approach**
- Introduce a simple, hypothetical cost curve.
- Compare marginal benefit against marginal cost.
- Identify regions where investment efficiency drops.

**Outputs**
- Scenario-based break-even illustrations.
- Narrative guidance for interpreting diminishing returns.
- Explicit separation between analysis and decision authority.

---

## 8. Data strategy

All data used in this project is synthetic.

The data-generating process is designed to:
- include realistic confounding,
- include feedback loops where appropriate,
- allow ground-truth validation of estimators.

Synthetic data is used intentionally to:
- make assumptions explicit,
- enable method comparison,
- avoid domain leakage.

---

## 9. Success criteria

This project is successful if:

- A Product Manager can read the README and follow the reasoning without prior causal inference training.
- A data science reviewer can clearly see:
  - identification logic,
  - estimator choice rationale,
  - limitations and failure modes.
- The project remains focused on decision support rather than metric absolutism.

---

## 10. Risks and mitigations

**Risk:** Overclaiming decision authority  
→ *Mitigation:* Clear labeling of assumptions and scenario-based framing.

**Risk:** Drifting into employer-specific territory  
→ *Mitigation:* Abstract naming, synthetic data, generic examples only.

**Risk:** Tool-driven rather than question-driven analysis  
→ *Mitigation:* PRD-first workflow (this document).

---

## 11. Open questions (to resolve early)

- Final choice of downstream outcomes (limit to 2–3).
- Level of heterogeneity analysis (simple vs richer).
- Primary estimator emphasis (EconML vs DoubleML).
- Reporting format (notebook-only vs generated Markdown).

---

## 12. Definition of done (v1)

- Stage 1 and Stage 2 fully implemented.
- Stage 3 included as decision framing, not recommendation.
- README reflects PRD intent.
- Assumptions and limitations are explicit.