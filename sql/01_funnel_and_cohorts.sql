-- Works in SQLite. All records synthetic.
-- 1. Observe application -> approval -> activation by experiment arm.
SELECT assigned_offer, COUNT(*) as prospects,
       SUM(applied) as applications,
       ROUND(1.0*SUM(applied)/COUNT(*),4) as application_conversion,
       SUM(approved) as approved,
       ROUND(1.0*SUM(approved)/NULLIF(SUM(applied),0),4) as conditional_approval,
       SUM(activated) as active_cards,
       ROUND(1.0*SUM(activated)/NULLIF(SUM(approved),0),4) as conditional_activation,
       ROUND(SUM(observed_net_contribution),2) as synthetic_first_year_contribution
FROM acquisition GROUP BY assigned_offer;

-- 2. Prevent Simpson's paradox: compare within preassigned customer segment.
SELECT segment,assigned_offer,COUNT(*) as prospects,
       ROUND(AVG(applied),4) as application_conversion,
       ROUND(AVG(activated),4) as card_activation_per_prospect,
       ROUND(AVG(observed_net_contribution),2) as contribution_per_lead
FROM acquisition GROUP BY segment,assigned_offer ORDER BY segment,assigned_offer;

-- 3. Time trend, check arm balance and cohort drift.
SELECT month,assigned_offer,COUNT(*) AS contacts,ROUND(AVG(applied),4) AS response_rate
FROM acquisition GROUP BY month,assigned_offer ORDER BY month,assigned_offer;
