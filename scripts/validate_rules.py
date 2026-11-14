#!/usr/bin/env python3
"""Release gate: no approved, current matching primary-source rules => nonzero."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
from decision_engine import load_rules, evidence_gate, RULE_FILE
from policy_engine import PolicyIndex, DATA_DIR

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--rules',type=Path,default=RULE_FILE);parser.add_argument('--index',type=Path,default=DATA_DIR/'index.sqlite3')
 args=parser.parse_args();rules=load_rules(args.rules);index=PolicyIndex(args.index)
 required={'fhtb','meals','mileage'};valid=set();report=[]
 for rule in rules:
  ok,reason=evidence_gate(rule,index);report.append({'id':rule.get('id'),'category':rule.get('category'),'valid':ok,'reason':reason})
  if ok:valid.add(rule.get('category'))
 missing=sorted(required-valid)
 ambiguous=sorted(c for c in required if sum(1 for r in rules if r.get('category')==c)>1)
 if any(r.get('category')=='fhtb' and not r.get('claim_process_verified') for r in rules):missing=sorted(set(missing)|{'fhtb.application_process'})
 print(json.dumps({'rule_gate_passed':not missing and not ambiguous,'release_ready':False,'manual_release_review_required':['current tax/RLE coverage','primary-source and exceptions sign-off','physical Android and hosted deployment verification'],'ambiguous_categories':ambiguous,'missing_verified_categories':missing,'rules':report},indent=2))
 sys.exit(1 if missing or ambiguous else 0)
