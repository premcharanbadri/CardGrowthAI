"""Rebuild from scratch: python -m src.run_pipeline"""
import json
from pathlib import Path
import joblib,numpy as np,pandas as pd
from sklearn.metrics import brier_score_loss,log_loss
from src.core import *
from src.experiment import two_proportions,approximate_sample_per_arm
R=Path(__file__).resolve().parents[1]
for d in ('data','models','outputs','docs/assets'):(R/d).mkdir(exist_ok=True,parents=True)
print('Step 1: synthetic three-arm randomized campaign, 12 months x 4,000 leads')
df=simulate();train,val,test=splits(df)
df.to_csv(R/'data/synthetic_acquisition_experiment.csv',index=False,float_format='%.8f')
print('Step 2: logistic baseline and nonlinear gradient-boosting challenger')
models_by={k:fit_models(train,k) for k in ('logistic','boosting')}
summary={'data':{'rows':len(df),'train':len(train),'validation':len(val),'test':len(test),
                 'unique_leads':int(df.lead_id.nunique()),'assignment':'uniform, randomized across 3 arms',
                 'date_range':'January-December 2025'},'arms':ARMS,'results':{},
         'assumptions':{'monthly_prospect_flow':4000,'holdout_contacts_cap':2600,'holdout_contact_budget':2600,
              'cashflow_cost_per_contact':.7,'rewards_cost_per_contact':1.1,
              'cashflow_cost_per_active_account':18,'incremental_rewards_per_annual_spend_dollar':.0012,
              'model_outcome':'application conversion','financial_horizon':'first-year modeled contribution, not lifetime value'}}
for label,data in [('validation',val),('test',test)]:
    summary['results'][label]={}
    for kind,models in models_by.items():
        prob=predict(models,data)
        policy,details=optimize(data,prob)
        diagnostics={}
        for a in range(3):
            mask=data.assigned_arm.to_numpy()==a
            y=data.applied.to_numpy()[mask]
            diagnostics[ARMS[a]]={'n':int(mask.sum()),'observed_conversion':round(float(y.mean()),5),
                    'brier':round(float(brier_score_loss(y,prob[mask,a])),5),
                    'logloss':round(float(log_loss(y,prob[mask,a])),5)}
        summary['results'][label][kind]={'policy':details,'simulation_oracle':oracle_evaluation(data,policy),
                                         'off_policy_ipw':ipw_evaluation(data,policy),'offer_model_fit':diagnostics}
        print(label,kind,'simulation-gain',summary['results'][label][kind]['simulation_oracle']['incremental'],
              'IPW',summary['results'][label][kind]['off_policy_ipw']['estimate'])
# Pre-register a conservative model selection rule using ONLY validation outcomes.
# Bootstrap-like paired influence comparison would also be appropriate; use analytic SE here.
problog=predict(models_by['logistic'],val)
probboost=predict(models_by['boosting'],val)
plog,_=optimize(val,problog)
pboost,_=optimize(val,probboost)
assigned=val.assigned_arm.to_numpy()
reward=val.observed_net_contribution.to_numpy()
paired=3*reward*((assigned==pboost).astype(float)-(assigned==plog).astype(float))
adv=float(paired.sum());adv_se=float(paired.std(ddof=1)*np.sqrt(len(paired)))
selected='boosting' if adv-1.96*adv_se>0 and adv>0.1*abs(summary['results']['validation']['logistic']['off_policy_ipw']['estimate']) else 'logistic'
summary['selected']=selected
summary['model_selection']={'rule':'Prefer logistic unless boosting has statistically persuasive positive incremental validation IPW uplift (one-sided positive 95% two-sided lower bound and 10% uplift).',
 'boosting_minus_logistic_validation_IPW':round(adv,2),'se':round(adv_se,2),
 'ci95_lower':round(adv-1.96*adv_se,2),'ci95_upper':round(adv+1.96*adv_se,2),
 'caveat':'High variance and correlated comparison; do not treat as real-world evidence.'}
models=models_by[selected]
for a in range(3):joblib.dump(models[a],R/f'models/{selected}_arm{a}.joblib')
prob=predict(models,test)
policy,details=optimize(test,prob)
output=test.drop(columns=['oracle_p0','oracle_p1','oracle_p2']).copy()
for a in range(3):output[f'estimate_application_arm{a}']=np.round(prob[:,a],6)
output['recommended_marketing_arm']=policy
output.to_csv(R/'outputs/holdout_offer_scoring.csv',index=False)
armtest=test.groupby('assigned_offer').agg(leads=('lead_id','count'),applications=('applied','sum'),
                        approved=('approved','sum'),activated=('activated','sum'),
                        synthetic_contribution=('observed_net_contribution','sum')).reset_index()
armtest['application_rate']=armtest.applications/armtest.leads
armtest['approval_rate']=armtest.approved/armtest.applications
armtest['activation_rate']=armtest.activated/armtest.approved
summary['holdout_observed_arms']=armtest.to_dict('records')
control=armtest[armtest.assigned_offer=='Standard'].iloc[0]
summary['experiment_significance']={}
for label in ['Cash-flow experience','Rewards experience']:
    grp=armtest[armtest.assigned_offer==label].iloc[0]
    summary['experiment_significance'][label]=two_proportions(int(control.applications),int(control.leads),int(grp.applications),int(grp.leads))
summary['experiment_design']={'alpha_per_comparison':.05,'power_target':.8,
  'required_per_arm_for_1pp_abs_lift':approximate_sample_per_arm(absolute_effect=.01),
  'required_per_arm_for_2pp_abs_lift':approximate_sample_per_arm(absolute_effect=.02),
  'caution':'Illustrative two-arm power; multiple arms require multiplicity adjustment; conversions not enough to prove profitable lift.'}
# Fair policy benchmarks: budget-appropriate random vs model and oracle; all-arm scenarios are unconstrained.
rng=np.random.default_rng(SEED+77)
n=len(test)
rand=np.zeros(n,dtype=int);indices=rng.choice(n,2600,replace=False);rand[indices]=rng.choice([1,2],len(indices))
true_prob=test[['oracle_p0','oracle_p1','oracle_p2']].to_numpy()
ideal,_=optimize(test,true_prob)
summary['holdout_benchmarks']={
  'all_standard':oracle_evaluation(test,np.zeros(n,dtype=int)),
  'random_budgeted':oracle_evaluation(test,rand),
  'selected_model':oracle_evaluation(test,policy),
  'unattainable_simulation_oracle':oracle_evaluation(test,ideal),
  'all_cashflow_unconstrained':oracle_evaluation(test,np.ones(n,dtype=int)),
  'all_rewards_unconstrained':oracle_evaluation(test,np.full(n,2,dtype=int))}
seg_results=[]
for seg,part in test.groupby('segment'):
    idx=np.flatnonzero(test.segment.to_numpy()==seg)
    pp=policy[idx]
    seg_results.append({'segment':seg,'leads':len(part),'targeted':int((pp>0).sum()),
      'cashflow':int((pp==1).sum()),'rewards':int((pp==2).sum()),
      'simulated_expected_incremental':oracle_evaluation(part,pp)['incremental']})
summary['segments']=seg_results
with open(R/'outputs/metrics.json','w') as f:json.dump(summary,f,indent=2)
# Browser data embeds scores, NOT oracle or observed individual outcomes.
browser={'summary':summary,'points':[{'s':int({'Cash-flow constrained':0,'Growth-focused':1,'Spend-intensive':2}[r.segment]),
 'p':[round(float(prob[i,j]),5) for j in range(3)],
 'a':round(float(r.approval_assumption*r.activation_assumption),5),
 'm':round(float(r.base_margin),2),'v':round(float(r.annual_spend),2)} for i,r in enumerate(test.itertuples(index=False))]}
with open(R/'docs/assets/data.json','w') as f:json.dump(browser,f,separators=(',',':'))
print('Step 3 complete:',len(output),'out-of-time simulated holdout leads; selected',selected)
