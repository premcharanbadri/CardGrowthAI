"""CardGrowth AI interactive portfolio dashboard. Deploy app.py on Streamlit Community Cloud.
All data is synthetic. No external APIs or credentials required.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.core import optimize,oracle_evaluation,CONTACT_COST,CASHFLOW_SERVICE_COST,REWARD_RATE

ROOT=Path(__file__).parent
st.set_page_config(page_title='CardGrowth AI | Strategy Lab',page_icon='📊',layout='wide')
@st.cache_data

def load():
  test=pd.read_csv(ROOT/'outputs/holdout_offer_scoring.csv')
  metrics=json.loads((ROOT/'outputs/metrics.json').read_text())
  p=test[[f'estimate_application_arm{x}' for x in range(3)]].to_numpy()
  return test,metrics,p

test,summary,p=load()
st.title('CardGrowth AI | Small-Business Card Strategy Lab')
st.caption('Independent applied analytics portfolio | 48,000 synthetic randomized leads | No customer data, no actual marketing or credit decisions')
st.warning('Every lead, application, approval, financial figure, and model result is synthetic. Projected values are NOT realized revenue or real experiment results.',icon='⚠️')

with st.sidebar:
  st.header('Strategy assumptions')
  budget=st.slider('Campaign budget ($)',0,6500,2600,100)
  max_contacts=st.slider('Maximum treated prospects',0,8000,2600,100)
  cashflow_contact=st.slider('Cash-flow outreach cost per lead ($)',.1,2.5,.7,.1)
  rewards_contact=st.slider('Rewards outreach cost per lead ($)',.1,3.,1.1,.1)
  service=st.slider('Cash-flow annual service cost per active card ($)',0,80,18,2)
  rewardbps=st.slider('Extra rewards cost (bps of annual card spend)',0,30,12,1)
  annual_fee=st.slider('Illustrative uniform annual fee ($)',0,120,0,5)
  elasticity=st.slider('Application reduction (percentage points / $100 annual fee)',0.,4.,1.2,.25)
  st.caption('The annual fee and its demand elasticity are illustrative product hypotheses, not differentiated credit prices.')

# Multi-arm response probabilities with optional hypothetical demand response to a uniform fee.
mod_p=np.clip(p-annual_fee/100*(elasticity/100),0,1)
ap=test.approval_assumption.to_numpy()*test.activation_assumption.to_numpy()
base=test.base_margin.to_numpy();spend=test.annual_spend.to_numpy()
contribution=np.column_stack([base+annual_fee,base+annual_fee-service,base+annual_fee-rewardbps/10000*spend])
contact=np.array([0,cashflow_contact,rewards_contact])
profits=mod_p*contribution*ap[:,None]-contact[None,:]
individual_gain=profits[:,1:]-profits[:,[0]]
best=1+np.argmax(individual_gain,axis=1)
gains=individual_gain[np.arange(len(best)),best-1]
policy=np.zeros(len(best),dtype=int);spent=0.;used=0
for i in np.argsort(-gains,kind='stable'):
  a=best[i]
  if gains[i]<=0 or used>=max_contacts:break
  if spent+contact[a]>budget:continue
  policy[i]=a;spent+=contact[a];used+=1
value=float((profits[np.arange(len(test)),policy]-profits[:,0]).sum())

m1,m2,m3,m4=st.columns(4)
m1.metric('Predicted incremental first-year contribution',f'${value:,.0f}')
m2.metric('Targeted prospects',f'{used:,}')
m3.metric('Campaign contact spend',f'${spent:,.0f}')
m4.metric('Projected contribution / contact spend',f'{value/spent:.1f}x' if spent else 'n/a')

tab1,tab2,tab3,tab4=st.tabs(['Experiment','Offer allocation','Financial scenarios','Evidence & governance'])
with tab1:
  st.subheader('Simulated randomized holdout experiment')
  arm=pd.DataFrame(summary['holdout_observed_arms'])
  arm=arm.set_index('assigned_offer').loc[['Standard','Cash-flow experience','Rewards experience']].reset_index()
  st.plotly_chart(px.bar(arm,x='assigned_offer',y='application_rate',text='application_rate',title='Application conversion by randomized arm',labels={'application_rate':'Application rate','assigned_offer':'Offer'}),use_container_width=True)
  st.dataframe(arm[['assigned_offer','leads','applications','application_rate','approved','activated']],hide_index=True,use_container_width=True)
  for name,res in summary['experiment_significance'].items():
    st.markdown(f"**{name}:** +{res['absolute_percentage_point_lift']:.2f} pp, unadjusted 95% CI [{res['ci95_pp'][0]:.2f}, {res['ci95_pp'][1]:.2f}] pp, p={res['p_value_unadjusted']:.4f}.")
  st.info('The experiment addresses conversion response. It does not demonstrate realized lifetime value or portfolio profit. Multiplicity and selection must be considered.')
with tab2:
  offer_counts=pd.DataFrame({'Offer':['Standard','Cash-flow experience','Rewards experience'],
                             'Prospects':np.bincount(policy,minlength=3)})
  left,right=st.columns(2)
  with left:
    st.plotly_chart(px.bar(offer_counts,x='Offer',y='Prospects',text='Prospects',title='Recommended marketing experience distribution'),use_container_width=True)
  with right:
    counts=test.assign(targeted=policy>0).groupby('segment',as_index=False).agg(leads=('lead_id','count'),targeted=('targeted','sum'))
    st.plotly_chart(px.bar(counts,x='segment',y=['leads','targeted'],barmode='group',title='Eligible segments and targeting'),use_container_width=True)
  st.caption('Selection is a greedy budget heuristic and excludes direct credit-approval decisions. Policy effectiveness requires experimental validation.')
with tab3:
  st.subheader('Unit economics, not application volume, drives targeting')
  comparison=pd.DataFrame({'Strategy':['Standard (base)','Configured policy'],
       'Expected annual modeled contribution ($)':[float(profits[:,0].sum()),float(profits[np.arange(len(test)),policy].sum())]})
  st.dataframe(comparison.style.format({'Expected annual modeled contribution ($)':'${:,.0f}'}),hide_index=True,use_container_width=True)
  st.markdown('**Model equation**')
  st.latex(r'EV_{i,a}=P(Apply_{i,a})\times P(Approve_i)\times P(Activate_i)\times Contribution_{i,a}-ContactCost_a')
  st.markdown('**Scenarios:** raise the rewards cost or outreach cost, and see whether the offer still creates incremental value. Change the uniform annual fee only as a hypothesis: its customer demand penalty is not estimated from live data.')
with tab4:
  st.subheader('Model and experiment discipline')
  selected=summary['selected'];res=summary['results']['test'][selected]
  st.write('Selected:',selected,'via prespecified validation model-complexity safeguard.')
  st.write('Synthetic simulator known oracle expected increment (base scenario):',f"${res['simulation_oracle']['incremental']:,.2f}")
  ipw=res['off_policy_ipw']
  st.write('Randomized off-policy profit estimate (base scenario):',f"${ipw['estimate']:,.2f}")
  st.write('Approximate 95% confidence interval:',f"[${ipw['ci95_low']:,.2f}, ${ipw['ci95_high']:,.2f}]")
  st.error('Confidence interval crosses zero. No causal profitability claim or implementation approval is justified.')
  st.markdown('**Go/no-go:** Run a larger, powered, pre-registered experiment. Gate rollout on incremental activated-card contribution, credit-quality guardrails, fair-lending review, marketing consent, complaints, and monitoring.')
  st.caption('No protected traits were generated. Their absence does not substitute for real-world fair lending review. This is a marketing allocation research project, not an underwriting model.')
