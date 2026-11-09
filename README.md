# CardGrowthAI : Small-Business Card Acquisition & Product Economics

## Executive question

How should a small-business-card issuer allocate a finite marketing budget among standard experience, cash-flow-tools onboarding, and rewards experience in order to improve **incremental first-year risk-adjusted contribution** rather than raw application volume?

**Why now?** The Federal Reserve's March 2026 Small Business Credit Survey reports that 86% of employer firms use financing regularly. Source: https://www.fedsmallbusiness.org/2026-report-on-employer-firms . This is market context only; **none** of the fabricated data or model parameters are estimated from the survey.

## Deliverables

- `docs/index.html` — polished, single-file interactive strategy lab; deploy with **GitHub Pages `/docs`** or **Cloudflare Pages**. It embeds 8,000 synthetic holdout predictions; it requires no Python server.
- `app.py` — alternative deeper Streamlit analytics dashboard, suited to Streamlit Community Cloud.
- `data/synthetic_acquisition_experiment.csv` — 48,000 randomized, synthetic leads across January–December 2025, with train/validation/test indicators inferred from month.
- `src/core.py` — reproducible randomized generator, three-arm T-learners, exposure- and cost-constrained greedy policy, simulation-oracle evaluation, randomized Horvitz–Thompson off-policy estimator.
- `src/pricing.py` — uniform annual-fee demand-elasticity **hypothesis**, not personalized price/underwriting.
- `src/exact_optimizer.py` — exact mixed-integer optimization benchmark with SciPy MILP.
- `src/experiment.py` — randomization test statistics and simple power estimate.
- `outputs/metrics.json` — model comparison, holdout, uncertainty, benchmarks, selection rationale.
- `outputs/holdout_offer_scoring.csv` — test predictions, selected policy, synthetic funnel outcomes (simulation oracle *excluded*).
- `outputs/milp_benchmark.json` — exact vs greedy constraint benchmark.
- `CardGrowth_AI_Financial_Model.xlsx` — linked financial assumptions, policy economics, pricing sensitivities, evidence audit, executive recommendation.
- `sql/01_funnel_and_cohorts.sql` — SQLite-compatible funnel and cohort analysis.
- `tests/test_core.py` — deterministic unit checks.
- `DECISION_MEMO.md`, `DATA_DICTIONARY.md`, `DEPLOY.md` — executive communication and audit artifacts.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m src.run_pipeline
python -m src.build_static
python -m unittest discover -s tests -v
streamlit run app.py
```

Open `docs/index.html` directly in a browser for a server-free case study.

## Scientific design and key assumptions

- **Experiment:** 48,000 leads, randomized 1:1:1 into three **marketing** experience arms; no different underwriting decision, individual APR, or credit line.
- **Training:** Jan–Aug 2025 (32,000). **Validation:** Sep–Oct 2025 (8,000). **Test:** Nov–Dec 2025 (8,000). Each lead is distinct; these are not 48,000 actual customers.
- **Response models:** logistic-regression T-learner versus histogram gradient-boosting T-learner. The learner estimates arm-specific response probabilities, not a causal uplift guaranteed to generalize. Any uplift is a *difference between estimated outcomes* under experimental assumptions.
- **Selection rule:** choose the more complex model only if its policy shows convincing improvement on validation data (paired randomized off-policy estimate with a positive 95% lower bound and >10% relative improvement); otherwise prefer simpler model. The final holdout is not used in model choice.
- **Value equation:** `P(application | arm) * P(approval | eligible application) * P(activation | approved) * modeled first-year margin(arm) - offer outreach cost`. Approval/activation probabilities are simulation assumptions. `First-year margin` contains synthetic spend yield and a simplified risk-cost proxy, **not true PD/EAD/LGD**, and is **not lifetime value**.
- **Policy:** send an alternative only when its estimated incremental contribution is positive. Select offers with a greedy highest-gain heuristic under max contacts and total cost. This does not guarantee global optimality.
- **Ground-truth oracle:** because the test data was *simulated*, the synthetic generator's counterfactual expected probabilities allow an **unattainable in-real-life simulation diagnostic**. Its evaluation is not proof of model behavior on actual card customers.
- **Causal estimate:** randomized Horvitz–Thompson IPW comparing selected policy versus all standard. Uncertainty is large; confidence interval spans zero. Normal approximation does not account for monthly clustering. Real policy evaluation needs randomized holdout and uncertainty-appropriate inference.
- **Fee/pricing:** only a hypothetical uniform annual-fee elasticity sensitivity. No individualized APR recommendations, adverse-action decisions, or credit approvals.

## Key reproducible results (synthetic holdout)

| Measure | Value |
|---|---:|
| Standard conversion (randomized) | 11.59% |
| Cash-flow conversion | 14.35% |
| Rewards conversion | 13.13% |
| Selected logistic-policy contacts | 2,600 of 8,000 |
| Contact spending | $2,290.80 |
| **Model-predicted first-year incremental contribution** | **$50,146.84** |
| **Simulation-oracle expected incremental contribution** | **$23,483.81** |
| Randomized off-policy estimate | $766.77 |
| 95% IPW confidence interval | **−$65,510.22 to +$67,043.76** |
| Small-subset exact MILP vs greedy improvement | **$29.96 / +1.91%** |

**Decision:** Do *not* roll out based on these simulated figures. Pilot the cash-flow experience with pre-registered decision thresholds and guardrails, while collecting enough evidence about activated-account contribution, customer benefit, credit quality, fairness, and operational feasibility. Reward messaging remains a candidate for selective testing rather than blanket promotion.

## Responsible execution

1. Only use approved, consensually obtained marketing prospect data with documented purpose and retention limits.
2. Avoid protected traits and impermissible proxies in marketing allocation; independent fair-lending review is still necessary. Their absence in this toy data is not compliance assurance.
3. Keep AI strictly advisory; do not automate lending decisions, APRs, underwriting, or adverse-action explanations.
4. Track conversion, approval, activation, incremental first-year contribution, retention, complaints, opt-outs, and model drift by authorized segments.
5. Maintain experiment logs, data lineage, challenge results, human approvals, and rollback triggers.
6. Consider a more powerful randomized policy evaluation (e.g. doubly robust estimation) and a full-scale mixed-integer solver only after establishing real data and business feasibility.

Regulatory context: https://www.consumerfinance.gov/1071-rule/ (check current scope and applicability)
