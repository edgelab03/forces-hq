"""Single in-session question handoff used by Home, entitlements and tools."""

def question_handoff(state, question, policy_page):
    question=question.strip()[:1500]
    state['active_question']=question
    key=f'input:{policy_page}:guided_search'
    state[key]=question
    known=state.setdefault('_input_keys',[])
    if key not in known:known.append(key)
    return question


def linked_milestones(profile,events):
    """One timeline view; keep original profile promotions and events intact."""
    return sorted([{'label':'Promotion: '+e['rank'],'date':str(e['date'])} for e in profile.get('rank_history',[])]+[{'label':e['label'],'date':str(e['date'])} for e in events],key=lambda e:e['date'])


def apply_restored_profile(state, restored, policy_profile_page):
    """Apply imported context before widgets render, including visible drafts.

Deleting an already-rendered widget key alone lets the browser send its previous
value back on the next rerun. Explicit assignments are intentional for a restore.
"""
    state['profile']={**state['profile'],**restored['profile']}
    state['events']=restored['events']
    from benefit_journeys import restore_benefits
    state['benefits']=restore_benefits(restored.get('benefits'))
    from benefit_journeys import TASKS
    progress=state['benefits']['fhtb']
    for key in list(state.get('_input_keys',[])):
        if key.startswith('input:journey:fhtb:'):state.pop(key,None)
    restored_widgets={'interested':progress['interested'],'completed':progress['completed'],'nation':progress['nation']}
    restored_widgets.update({'task:'+key:progress['checklist'].get(key,False) for key in TASKS})
    restored_widgets.update({'budget:'+key:progress['budget'].get(key,10 if key=='years' else 5.0 if key=='mortgage_rate' else 0.0) for key in ('price','deposit','advance','mortgage','tax','legal','survey','searches','registration','other','years','mortgage_rate')})
    for key,value in restored_widgets.items():state['input:journey:fhtb:'+key]=value
    state['fhtb_edit_budget']=False

    state['profile_applied']=True
    state['profile_saved']=True
    p=state['profile']
    fields={
      'v06_service':p['service'],'v06_rank':p['rank'],'v06_years':p['years'],
      'v06_report':p['report'],'v06_transfer':p['transfer_history'],
      'v06_band':p['pay_supplement'] or 'Not selected','v06_point':p['pay_increment'] or 'Not selected',
      'v06_salary':int(p['verified_pensionable_salary'] or 0),'v06_salary_checked':p['salary_verified'],
      'v06_posting':p['posting'],'v06_family':p['family'],
      'v07_has_join':bool(p.get('join_date_set') or p.get('join_date')),'v07_join':p.get('join_date'),
      'v07_has_dob':bool(p.get('dob_set') or p.get('dob')),'v07_dob':p.get('dob'),
      'v07_employment':p['employment_type'],'v07_dep_count':p['dependent_count'],
      'v07_accom':p['accommodation_type'],'v07_schemes':p['pension_schemes'],
      'v07_has_exit':bool(p.get('planned_exit_set') or p.get('planned_exit')),'v07_exit':p.get('planned_exit'),
    }
    for name,value in fields.items():state[f'input:{policy_profile_page}:{name}']=value
