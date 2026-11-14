"""User-controlled encrypted profile files; no shared server-side user database.

Only structured context is persisted. Posting locations, names, free-text notes,
appraisals, questions and passwords are deliberately excluded.
"""
import base64
from datetime import date
import json
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC=b'FHQ1\n'
MAX_SIZE=128*1024
CHOICES={
 'service':['British Army','Royal Navy','Royal Air Force','Royal Marines'],
 'rank':['Private / equivalent','Lance Corporal / equivalent','Corporal / equivalent','Sergeant','Staff Sergeant','Warrant Officer','Commissioned Officer'],
 'report':['SJAR','OJAR'], 'employment_type':['Regular','Reserve','FTRS','Not specified'],
 'transfer_history':['None / not recorded','Transfer / break in service','Commissioned from ranks','Other history — check statement'],
 'posting':['Not specified','No planned move','Upcoming assignment / move'],
 'family':['Not specified','No dependants recorded','Dependants / children'],
 'accommodation_type':['Not specified','SFA','SLA','Private rented','Own home','Substitute accommodation','Other'],
}
FIELDS=set(CHOICES)|{'years','pay_supplement','pay_increment','verified_pensionable_salary','salary_verified','join_date','dob','planned_exit','join_date_set','dob_set','planned_exit_set','dependent_count','pension_schemes','rank_history'}
EVENT_LABELS=['Objectives agreed','MPAR','SJAR / OJAR drafting','SJAR / OJAR submission','Promotion / board window (verify)','Course / qualification','Posting / assignment','Other']

def validate(payload):
    if not isinstance(payload,dict) or payload.get('version')!=1 or not isinstance(payload.get('profile'),dict):
        raise ValueError('Unsupported profile backup')
    p=payload['profile']
    if set(p)-FIELDS:raise ValueError('Unexpected profile fields')
    for key,value in p.items():
        if key in CHOICES and value not in CHOICES[key]:raise ValueError('Unsupported '+key)
        if key in ('join_date','dob','planned_exit') and value is not None:
            if not isinstance(value,str):raise ValueError('Invalid date')
            parsed=date.fromisoformat(value)
            if not date(1940,1,1)<=parsed<=date(2080,12,31):raise ValueError('Date outside supported range')
            if key=='join_date' and parsed<date(1960,1,1):raise ValueError('Enlistment date outside supported range')
            if key in ('join_date','dob') and parsed>date.today():raise ValueError('Birth and enlistment dates cannot be in the future')
            p[key]=parsed
        if key in ('salary_verified','join_date_set','dob_set','planned_exit_set') and type(value) is not bool:raise ValueError('Invalid flag')
        if key in ('years','dependent_count','pay_supplement','pay_increment','verified_pensionable_salary'):
            if key in ('years','dependent_count') and value is None:raise ValueError('Missing required count')
            maximum={'years':45,'dependent_count':12,'pay_supplement':4,'pay_increment':20,'verified_pensionable_salary':300000}[key]
            if value is not None and (type(value) not in (int,float) or not 0<=value<=maximum):raise ValueError('Invalid numeric profile value')
            if key!='verified_pensionable_salary' and value is not None and type(value) is not int:raise ValueError('Expected whole number')
        if key=='rank_history':
            if not isinstance(value,list) or len(value)>300:raise ValueError('Invalid promotion timeline')
            for entry in value:
                if not isinstance(entry,dict) or set(entry)!={'rank','date'} or entry['rank'] not in CHOICES['rank']:raise ValueError('Invalid promotion')
                parsed=date.fromisoformat(entry['date'])
                if not date(1960,1,1)<=parsed<=date.today():raise ValueError('Invalid promotion date')
                if p.get('join_date') and parsed<date.fromisoformat(str(p['join_date'])):raise ValueError('Promotion precedes enlistment')
        if key=='pension_schemes':
            if not isinstance(value,list) or len(value)>4 or any(s not in ['AFPS 75','AFPS 05','AFPS 15','RFPS 05','Not sure'] for s in value) or ('Not sure' in value and len(value)>1):raise ValueError('Invalid scheme selection')
    if p.get('dob') and p.get('join_date') and p['dob']>=p['join_date']:raise ValueError('Birth date must precede enlistment')
    if p.get('join_date') and p.get('planned_exit') and p['join_date']>=p['planned_exit']:raise ValueError('Exit must follow enlistment')
    events=payload.get('events',[])
    if not isinstance(events,list) or len(events)>300:raise ValueError('Too many milestones')
    for event in events:
        if not isinstance(event,dict) or set(event)!= {'label','date'} or event['label'] not in EVENT_LABELS:raise ValueError('Invalid milestone')
        event['date']=date.fromisoformat(event['date'])
        if not date(1940,1,1)<=event['date']<=date(2080,12,31):raise ValueError('Invalid milestone date')
    return payload


def _key(password,salt):
    kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=600000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))


def save(profile,events,password):
    if len(password)<12:raise ValueError('Use a passphrase of at least 12 characters')
    chosen={k:v for k,v in profile.items() if k in FIELDS}
    # Unknown/old accommodation vocabulary stays session-only rather than
    # silently weakening import validation.
    if chosen.get('accommodation_type') not in CHOICES['accommodation_type']:chosen.pop('accommodation_type',None)
    if 'rank_history' in chosen:chosen['rank_history']=[{'rank':e['rank'],'date':str(e['date'])} for e in chosen['rank_history']]
    payload={'version':1,'profile':chosen,'events':[{'label':e['label'],'date':str(e['date'])} for e in events]}
    raw=json.dumps(payload,default=str,allow_nan=False).encode()
    validate(json.loads(raw))
    if len(raw)>MAX_SIZE//2:raise ValueError('Profile backup is too large')
    salt=os.urandom(16)
    return MAGIC+salt+Fernet(_key(password,salt)).encrypt(raw)


def load(data,password):
    if not isinstance(data,bytes) or len(data)>MAX_SIZE or not data.startswith(MAGIC):raise ValueError('Invalid or oversized encrypted backup')
    try:
        salt=data[len(MAGIC):len(MAGIC)+16]
        payload=Fernet(_key(password,salt)).decrypt(data[len(MAGIC)+16:])
        return validate(json.loads(payload))
    except (InvalidToken,ValueError,TypeError,KeyError,OverflowError) as exc:
        raise ValueError('Cannot restore: incorrect passphrase, damaged file or invalid profile') from exc
