import unittest
import numpy as np
from src.core import *
from src.pricing import fee_scenario

class TestDecisionLab(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.df=simulate(90,seed=51)
  def test_randomization_and_arm_labels(self):
    self.assertEqual(len(self.df),1080)
    self.assertEqual(set(self.df.assigned_arm.unique()),{0,1,2})
    self.assertTrue((self.df.assignment_propensity==1/3).all())
  def test_funnel_monotonic(self):
    self.assertTrue((self.df.activated<=self.df.approved).all())
    self.assertTrue((self.df.approved<=self.df.applied).all())
  def test_training_no_oracle_leakage(self):
    self.assertFalse(any('oracle' in x for x in FEATURES))
    self.assertFalse(any(x in FEATURES for x in ['applied','approved','activated','observed_net_contribution']))
  def test_policy_respects_limits(self):
    prob=np.column_stack([np.full(len(self.df),.1),np.full(len(self.df),.3),np.full(len(self.df),.28)])
    choice,metrics=optimize(self.df,prob,budget=20,max_contacts=15)
    self.assertLessEqual(metrics['budget_spent'],20)
    self.assertLessEqual(metrics['contacts'],15)
    self.assertEqual(metrics['contacts'],int((choice>0).sum()))
  def test_no_profitable_intervention_keeps_control(self):
    prob=np.column_stack([np.full(len(self.df),.4),np.full(len(self.df),.05),np.full(len(self.df),.05)])
    choice,_=optimize(self.df,prob)
    self.assertEqual(int(choice.sum()),0)
  def test_oracle_baseline_consistency(self):
    chosen=np.zeros(len(self.df),dtype=int)
    calc=oracle_evaluation(self.df,chosen)
    self.assertEqual(calc['incremental'],0)
  def test_ipw_finite(self):
    choice=np.zeros(len(self.df),dtype=int)
    estimate=ipw_evaluation(self.df,choice)
    self.assertEqual(estimate['estimate'],0)
    self.assertTrue(np.isfinite(estimate['ci95_low']))
  def test_pricing_fee_sensitivity(self):
    p=np.full((len(self.df),3),.10)
    a=fee_scenario(self.df,p,annual_fee=0)
    b=fee_scenario(self.df,p,annual_fee=95,conversion_penalty_per_100=0)
    # With no demand response, a fixed annual fee should raise expected contribution.
    self.assertTrue(np.all(b>a))
  def test_chronological_split(self):
    tr,v,te=splits(self.df)
    self.assertTrue((tr.month_id<=8).all())
    self.assertTrue(v.month_id.between(9,10).all())
    self.assertTrue((te.month_id>=11).all())
if __name__=='__main__':unittest.main()
