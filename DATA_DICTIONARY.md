# Data Dictionary — Synthetic Acquisition Experiment

Each row is **one unique synthetic prospect** randomized to a marketing experience (not a credit decision). Source: `src/core.py`, seed 1926.

| Field | Definition | Role |
|---|---|---|
| lead_id | Synthetic prospect primary key | Identifier; excluded from predictive features |
| month / month_id | Synthetic marketing cohort Jan–Dec 2025 | Chronological splits and monitoring; excluded from model features |
| segment | Cash-flow constrained / Growth-focused / Spend-intensive | Generated business-need segmentation |
| channel | Direct / Partner / Search | Pre-exposure acquisition channel |
| industry | Synthetic self-reported industry | Pre-exposure business context; would require real-world compliance assessment |
| firm_age_years | Simulated operating tenure | Pre-exposure predictor |
| annual_revenue | Synthetic annual sales estimate | Pre-exposure predictor, not verified credit exposure |
| annual_spend | Synthetic projected annual card spend | Pre-exposure predictor and margin driver |
| expense_volatility | Synthetic spend variability index 0–1 | Pre-exposure predictor; simplified risk-cost proxy |
| cashflow_need | Synthetic business cash-flow tools interest score | Pre-exposure predictor |
| digital_intent | Synthetic online engagement 0–1 | Pre-exposure predictor |
| prior_interest | Synthetic prior card product interaction (0/1) | Pre-exposure predictor |
| assigned_arm / assigned_offer | Randomized 0 standard, 1 cash-flow, 2 rewards | Experiment treatment; excluded from predictors other than separate per-arm training |
| assignment_propensity | Exactly 1/3 by design | Needed for off-policy causal estimator |
| applied | Application submitted within synthetic attribution window | Training label / experiment response |
| approved | Application approved in simulator | Downstream observed outcome (NOT used as application model input) |
| activated | Approved card activated in simulator | Downstream observed outcome |
| approval_assumption | Simulated approval probability | Economic model assumption; NOT a real underwriting model |
| activation_assumption | Simulated activation probability | Economic model assumption |
| base_margin | Synthetic first-year per-activated-card contribution net of servicing & simplified risk proxy | Economic scenario only; NOT net present value or real revenue |
| observed_net_contribution | Activated × offer margin − randomized marketing contact cost | Synthetic logged reward for randomized policy evaluation |
| oracle_p0 / oracle_p1 / oracle_p2 | TRUE synthetic response-generating probabilities for each arm | Simulator diagnostic **only**, strictly excluded from fitting and deployed scoring |
| estimate_application_arm0/1/2 | Calibrated? No: basic T-learner predicted response probability per arm | Model estimation; probability calibration NOT guaranteed |
| recommended_marketing_arm | Chosen 0/1/2 under spend and contact limits | Suggested marketing experience only; no lending decision |

## Treatment economics

- Standard: no incremental contact cost.
- Cash-flow: $0.70 per prospect contacted + $18 per activated account for additional service capabilities.
- Rewards: $1.10 per prospect contacted + 0.12% of modeled annual spend per activated account.
- Base annual contribution: clipped `(0.82% × annual_spend − $72 servicing − $45 × volatility risk proxy)`.
- These are **illustrative financial parameters** and need issuer-specific cost and revenue models before any real decision.

## Leakage and governance

The predictive feature list in `src/core.py` excludes assignment, responses, approval, activation, and all oracle labels. The financial model uses simulated approval and activation rates as scenario factors, not as predictions of actual applicants. No protected traits or actual clients are present, and their absence is not a substitute for independent fair lending or representativeness analysis.
