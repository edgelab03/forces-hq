"""Synthetic decision specifications test safety; they are NOT military policy."""
from copy import deepcopy
from datetime import date
from pathlib import Path
import hashlib
import tempfile
import unittest
from policy_engine import PolicyIndex, write_index
from decision_engine import assess, evidence_gate, advance_limit, benefit_result, repayment_estimate, purchase_budget, ELIGIBLE, INELIGIBLE, MORE, UNVERIFIED

QUOTE='Synthetic TEST ONLY condition: duty context and provided meals must be assessed. This invented test document establishes no real entitlement.'
DIGEST=hashlib.sha256(QUOTE.encode()).hexdigest()

def synthetic_rule(category='meals'):
 return {'id':'SYNTHETIC-TEST-ONLY','category':category,'version':'TEST-v1','review_status':'approved','reviewed_by':'TEST FIXTURE, not a policy reviewer','reviewed_on':'2026-01-01','effective_from':'2026-01-01','review_until':'2080-01-01','exceptions_reviewed':True,'coverage_complete':True,
  'evidence':[{'source_id':'TEST ONLY','title':'Synthetic fixture, not policy','chapter':'CHAPTER 99 TEST ONLY','section':'SECTION 98 TEST ONLY','paragraph':'99.9801','quote':QUOTE,'document_version':'TEST ONLY','page':1,'url':'https://assets.publishing.service.gov.uk/synthetic-not-policy.pdf','sha256':DIGEST}],
  'conditions':[
   {'fact':category+'.duty','operator':'eq','value':'Yes','options':['Yes','No'],'question':'Synthetic test duty condition?','evidence_index':0,'failure_reason':'Test duty condition is not met.'},
   {'fact':category+'.provided','operator':'eq','value':'No','options':['Yes','No'],'question':'Synthetic test provided-meal condition?','evidence_index':0,'failure_reason':'Test provided-meal condition is not met.'}],
  'financials':{'salary_fraction':.5,'advance_cap':25000,'salary_fact':'profile.salary','salary_basis':'SYNTHETIC TEST basis, not an official scheme salary definition'},'financials_evidence_index':0,'claim_steps':[]}

def fact(value):return {'value':value,'provenance':'user_confirmed'}

class DecisionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  path=Path(self.temp.name)/'index.sqlite3';self.index=PolicyIndex(path)
  write_index(path,[{'source_id':'TEST ONLY','document_id':'synthetic','title':'TEST ONLY','url':'https://assets.publishing.service.gov.uk/synthetic-not-policy.pdf','retrieved_at':date.today().isoformat(),'sha256':DIGEST,'pages':['CHAPTER 99 TEST ONLY\nSECTION 98 TEST ONLY\n99.9801. '+QUOTE]}])
  self.rule=synthetic_rule()
 def evaluate(self,category,facts,index,rules):
  return assess(category,{category+'.incident_date':fact(date.today().isoformat()),**facts},index,rules)
 def test_source_gate_precedes_any_eligibility_or_questions(self):
  result=self.evaluate('meals',{'meals.duty':fact('Yes'),'meals.provided':fact('No')},self.index,rules=[])
  self.assertEqual(result['status'],UNVERIFIED);self.assertEqual(result['missing'],[])
 def test_missing_conditions_then_preliminary_assessment(self):
  result=self.evaluate('meals',{},self.index,[self.rule]);self.assertEqual(result['status'],MORE);self.assertEqual(len(result['missing']),2)
  result=self.evaluate('meals',{'meals.duty':fact('Yes')},self.index,[self.rule]);self.assertEqual(len(result['missing']),1)
  result=self.evaluate('meals',{'meals.duty':fact('Yes'),'meals.provided':fact('No')},self.index,[self.rule]);self.assertEqual(result['status'],ELIGIBLE);self.assertTrue(result['preliminary'])
 def test_exceptions_and_failed_conditions_have_evidence(self):
  result=self.evaluate('meals',{'meals.duty':fact('No')},self.index,[self.rule]);self.assertEqual(result['status'],INELIGIBLE);self.assertIn('not met',result['reason']);self.assertEqual(result['trace'][0]['evidence_index'],0)
 def test_private_and_wo1_have_identical_circumstance_outcomes(self):
  for rank in ['Private / equivalent','Warrant Officer']:
   result=self.evaluate('meals',{'profile.rank':fact(rank),'meals.duty':fact('Yes'),'meals.provided':fact('No')},self.index,[self.rule]);self.assertEqual(result['status'],ELIGIBLE)
 def test_stale_unreviewed_changed_and_missing_sources_abstain(self):
  variants=[]
  for key,value in [('review_until','2020-01-01'),('review_status','draft'),('coverage_complete',False),('exceptions_reviewed',False),('reviewed_by','')]:
   r=deepcopy(self.rule);r[key]=value;variants.append(r)
  for field,value in [('quote','A quotation that is not in the original document and is fabricated.'),('sha256','0'*64),('paragraph','99.9999'),('url','https://evil.example/test.pdf')]:
   r=deepcopy(self.rule);r['evidence'][0][field]=value;variants.append(r)
  for rule in variants:self.assertEqual(self.evaluate('meals',{},self.index,[rule])['status'],UNVERIFIED)
 def test_seniority_alone_cannot_establish_entitlement(self):
  rule=deepcopy(self.rule);rule['conditions']=[{**rule['conditions'][0],'fact':'profile.rank','value':'Warrant Officer'}]
  self.assertEqual(self.evaluate('meals',{'profile.rank':fact('Warrant Officer')},self.index,[rule])['status'],UNVERIFIED)
 def test_unconfirmed_profile_facts_do_not_satisfy_conditions(self):
  result=self.evaluate('meals',{'meals.duty':{'value':'Yes','provenance':'example'}},self.index,[self.rule]);self.assertEqual(result['status'],MORE)
 def test_financial_caps_only_come_from_reviewed_rule(self):
  rule=synthetic_rule('fhtb');result=self.evaluate('fhtb',{},self.index,[rule])
  self.assertEqual(advance_limit(40000,result),20000);self.assertEqual(advance_limit(90000,result),25000)
  self.assertIsNone(advance_limit(40000,self.evaluate('fhtb',{},self.index,[])))
  rule.pop('financials_evidence_index');self.assertEqual(self.evaluate('fhtb',{},self.index,[rule])['status'],UNVERIFIED)
 def test_completed_benefits_are_not_promoted_as_eligible(self):
  result=benefit_result('fhtb',{},self.index,{'completed':True},[])
  self.assertEqual(result['status'],'Already claimed or completed');self.assertTrue(result['completed'])
 def test_unsupported_or_unverified_application_process_is_not_rendered(self):
  rule=deepcopy(self.rule);rule['claim_steps']=[{'text':'Invented step'}]
  self.assertEqual(self.evaluate('meals',{},self.index,[rule])['claim_steps'],[])
  rule['claim_process_verified']=True;self.assertEqual(self.evaluate('meals',{},self.index,[rule])['status'],UNVERIFIED)
 def test_generic_cashflow_and_purchase_budget_arithmetic(self):
  self.assertEqual(repayment_estimate(24000,10),200)
  self.assertAlmostEqual(repayment_estimate(100000,25,5),584.59,2)
  result=purchase_budget(200000,20000,10000,170000,2000,1500,500,300,200)
  self.assertEqual(result['shortfall'],4500);self.assertEqual(result['total_cost'],204500)
  for bad in [-1,float('nan'),float('inf')]:
   with self.assertRaises(ValueError):repayment_estimate(bad,10)

 def test_date_missing_and_wrong_version_do_not_issue_an_assessment(self):
  result=assess('meals',{},self.index,[self.rule]);self.assertEqual(result['status'],MORE);self.assertEqual(result['missing'][0]['input_type'],'date')
  result=assess('meals',{'meals.incident_date':fact('2020-01-01')},self.index,[self.rule]);self.assertEqual(result['status'],UNVERIFIED)
 def test_stated_yesterday_and_meal_are_reused_without_guessing_permission(self):
  from decision_engine import facts_from_question
  facts=facts_from_question('meals','Can I claim my lunch back yesterday?',date(2026,11,14))
  self.assertEqual(facts['meals.incident_date']['value'],'2026-11-13');self.assertEqual(facts['meals.type']['value'],'Lunch');self.assertNotIn('meals.duty',facts)

 def test_conditional_exception_asks_only_applicable_questions(self):
  rule=deepcopy(self.rule)
  rule['conditions'][1]['operator']='in';rule['conditions'][1]['value']=['Yes','No']
  rule['conditions'].append({'fact':'meals.exception','operator':'eq','value':'Yes','options':['Yes','No'],'question':'TEST ONLY exception?','evidence_index':0,'when':{'fact':'meals.provided','equals':'Yes'},'failure_reason':'Synthetic exception not met.'})
  common={'meals.duty':fact('Yes'),'meals.provided':fact('No')}
  self.assertEqual(self.evaluate('meals',common,self.index,[rule])['status'],ELIGIBLE)
  common['meals.provided']=fact('Yes')
  result=self.evaluate('meals',common,self.index,[rule]);self.assertEqual(result['status'],MORE);self.assertEqual([x['fact'] for x in result['missing']],['meals.exception'])
  common['meals.exception']=fact('No')
  result=self.evaluate('meals',common,self.index,[rule]);self.assertEqual(result['status'],INELIGIBLE);self.assertEqual(result['missing'],[])
