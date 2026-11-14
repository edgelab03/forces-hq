"""Connected, source-gated home-buying preparation, not an official application."""
from copy import deepcopy
from datetime import date
import math

FHTB_URL='https://www.gov.uk/guidance/forces-help-to-buy'
JSP464_URL='https://www.gov.uk/government/publications/jsp-464-tri-service-accommodation-regulations-tsars'
JSP752_URL='https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances'
TAX_LINKS={
 'England / Northern Ireland':('HMRC SDLT rates and guidance','https://www.gov.uk/stamp-duty-land-tax/residential-property-rates'),
 'Scotland':('Revenue Scotland LBTT','https://www.revenue.scot/taxes/land-buildings-transaction-tax/residential-property'),
 'Wales':('Welsh Government LTT','https://www.gov.wales/land-transaction-tax-rates-and-bands'),
}
STEPS=['Start','Assess','Budget','Prepare','Progress']
# These are preparation tasks, NOT claimed MOD application requirements.
TASKS={
 'read_scheme':'Read the current official FHTB guidance and confirm scheme conditions',
 'lender':'Ask the lender or broker whether the proposed funding is acceptable',
 'solicitor':'Obtain a conveyancing quote and ask about scheme documentation',
 'survey':'Compare survey options and costs for the property',
 'tax':'Obtain a property-tax calculation for the correct UK nation and buyer circumstances',
 'approval':'Confirm the authorised application route, deadlines and approval sequence with unit admin',
 'documents':'Confirm required forms, evidence and legal documentation against current instructions',
 'completion':'Confirm funding and legal arrangements before committing to completion',
 'rle':'Check Refund of Legal Expenses (New Buyer) separately; do not assume entitlement',
}
BUDGET_KEYS={'price','deposit','advance','mortgage','tax','legal','survey','searches','registration','other','years','mortgage_rate'}


def empty_progress():
 return {'step':'Start','completed':False,'interested':False,'checklist':{},'budget':{},'facts':{},'nation':'England / Northern Ireland'}


def validate_progress(value):
 if not isinstance(value,dict) or set(value)-{'step','completed','interested','checklist','budget','facts','nation'}:raise ValueError('Invalid benefit progress')
 result=empty_progress();result.update(deepcopy(value))
 if result['step'] not in STEPS or type(result['completed']) is not bool or type(result['interested']) is not bool or result['nation'] not in TAX_LINKS:raise ValueError('Invalid journey state')
 if not isinstance(result['checklist'],dict) or set(result['checklist'])-TASKS.keys() or any(type(v) is not bool for v in result['checklist'].values()):raise ValueError('Invalid checklist')
 if not isinstance(result['budget'],dict) or set(result['budget'])-BUDGET_KEYS:raise ValueError('Invalid budget fields')
 for name,number in result['budget'].items():
  if type(number) not in (int,float) or not math.isfinite(number) or not 0<=number<=10000000:raise ValueError('Invalid budget amount')
  if name=='years' and not 1<=number<=40:raise ValueError('Invalid repayment years')
  if name=='mortgage_rate' and not 0<=number<=30:raise ValueError('Invalid mortgage rate')
 # Only typed, non-identifying eligibility answers. Never persist free-text notes.
 if not isinstance(result['facts'],dict) or len(result['facts'])>40:raise ValueError('Invalid saved answers')
 for key,fact in result['facts'].items():
  if not isinstance(key,str) or not key.startswith(('fhtb.','meals.','mileage.')) or len(key)>70:raise ValueError('Unexpected fact')
  if not isinstance(fact,dict) or set(fact)!={'value','provenance'} or fact['provenance'] not in ('user_confirmed','user_stated','document_checked'):raise ValueError('Invalid fact provenance')
  val=fact['value']
  if type(val) not in (str,int,float,bool) or (isinstance(val,str) and (len(val)>80 or '\n' in val)):raise ValueError('Invalid fact value')
  if type(val) in (int,float) and not math.isfinite(val):raise ValueError('Invalid fact number')
 return result


def restore_benefits(data):
 if data is None:return {'fhtb':empty_progress()}
 if not isinstance(data,dict) or set(data)-{'fhtb'}:raise ValueError('Unsupported benefits')
 return {'fhtb':validate_progress(data.get('fhtb',{}))}
