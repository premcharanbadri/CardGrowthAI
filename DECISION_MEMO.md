# Decision Memo: Should We Scale the Personalized Card Acquisition Experience?

**To:** VP, Business Cards & Payments / Risk / Product / Marketing / Finance  
**From:** Business Analytics Strategy  
**Subject:** CardGrowth AI — synthetic portfolio experiment and investment recommendation  
**Evidence classification:** Synthetic case study, not real customers or financial impacts.

## Decision requested

Approve *design of a larger controlled pilot*, **not** broad launch or policy automation.

## Situation and competing hypotheses

Applying customers are not equivalent to profitable customers. A cash-flow-centered onboarding experience might attract businesses seeking better expense control, while a rewards-centered experience might resonate with high-spend firms. But both require servicing or rewards expense; they may reduce first-year contribution for some customers. Our hypotheses were that (H1) messages change application likelihood; (H2) response is heterogeneous by business need; (H3) targeting using expected contribution can outperform broad campaigns; and (H4) a complex AI model may or may not be better than a simple, explainable model.

## What the synthetic prototype did

Randomized 48,000 synthetic leads across Standard, Cash-flow, and Rewards arms. Used the first eight months for model fitting, two for validation and model selection, and the final two as an untouched test. Compared logistic and gradient-boosted T-learners, calculated expected first-year contribution after offer-related expenses, prioritized outreach within contact and spend budgets, and assessed final policy with an unbiased high-variance randomized off-policy estimator.

## Findings

- Simulated cash-flow conversion 14.35% versus 11.59% standard, +2.77pp; unadjusted 95% CI 0.96pp to 4.58pp. Rewards conversion 13.13% (+1.54pp); its interval includes zero.
- The more complex gradient boosting model failed to show a reliably positive benefit over logistic regression on validation. Prefer logistic for transparency and lower validation burden.
- Base-case predicted incremental contribution: **$50,146.84** on 2,600 marketed leads with $2,290.80 direct outreach spend. This is NOT a net firm cash ROI and does not include fixed program costs.
- Known simulator expectation: **$23,483.81**. Predicted economic value is **overstated** by the model in this synthetic experiment.
- Randomized off-policy estimate: **$766.77**; approximate 95% CI **−$65,510.22 to +$67,043.76**. Causal financial effectiveness is **not established**.
- On a 300-lead subset with a binding $50 budget, exact MILP improves modeled gain 1.91% over greedy targeting. More sophisticated optimization can help when budget is binding, but deployment depends on materiality, latency, interpretability, and controls.

## Recommended next decision

1. **No broad rollout:** profitability and customer outcomes have not been established.
2. **Pre-register a powered experiment:** prospect-level randomization, treatment exposure tracking, primary first-year incremental net contribution (with interim leading indicators), one-month retention, conversion-to-activation, credit-quality and complaints guardrails. Use multiplicity adjustment for 3 arms and sample size reflecting financial rather than only application outcomes.
3. **Test practical alternatives:** improve cash-flow messaging and onboarding before expensive dynamic pricing. Retain human oversight and transparent offer definitions.
4. **Finance partnership:** use actual approved cost-of-funds, rewards, interchange, acquisition spend, credit costs, and persistence assumptions to validate unit economics.
5. **Risk and compliance review:** document consent, segment eligibility, permitted marketing data, fair lending controls, and operational rollback.
6. **Monitoring:** application, approval, activation, retained accounts, incremental contribution per prospect, adoption, complaint rates, model drift, and missing-data rates; stop if customer or financial guardrails fail.

## What would change the decision?

A sufficiently powered randomized policy experiment showing a *positive, practically material, and statistically credible* incremental portfolio contribution with no material deterioration in credit-quality, customer treatment, or compliance outcomes.

## Limitations

All values are generated and do not describe Capital One, TCS, Prem's past work, or any issuer's actual performance. The test data-generating process is known only because it is a simulator. Observed conversion differences and model scores do not establish a real financial impact. Marketing policy does not determine creditworthiness, APR, approvals, or limits.
