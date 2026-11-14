# Policy retained-state TypeError hotfix

## Reproduction and limits of diagnosis

Base: production merge `9a8e2b8da3733e95f9c2e13c266201409944b1a5`.

The unmodified renderer reproduces:

```
app.py:382: render_question(p,navigate,PAGES,open_fhtb)
policy_ui.py:33: verified_profile_facts(profile,applied) | stored
TypeError: unsupported operand type(s) for |: 'dict' and 'NoneType'
```

Trigger: retain `active_question='Can I claim lunch?'`, `assessment_questions={'meals':'Can I claim lunch?'}` and `decision_facts={'meals':None}`, then navigate to Policy. Matching the cached question skips derivation, leaving `stored=None` for the dictionary union. `setdefault` repairs absent keys, not existing values of the wrong type. With a dated question the same invalid entry fails earlier with `TypeError: argument of type 'NoneType' is not iterable`. A legacy scalar incident date also reproduces `TypeError: string indices must be integers, not 'str'`.

Fresh-session queries at the reported merge did not reproduce a failure. The live URL is blocked by the environment proxy (CONNECT 403), and the final live TypeError message has been requested but not supplied. These are confirmed local retained-state failures; matching them to the exact live traceback remains unverified. In particular, an argument-count TypeError would be a different failure and needs the complete message.

## Fix

- Validate policy cache mappings before membership tests, mutation or fact union.
- Validate retained fact-record shape before indexing `['value']`.
- Keep malformed values in the same session's `_policy_cache_recovery` map; do not promote them to confirmed facts or clear the user's profile, unrelated topics or valid answers.
- Normalise a nullable retained question to an empty input.
- Preserve rendering, navigation, calculation and policy-rule behaviour. No redesign, dependencies or deployed-call signature changes.

## Validation

- New retained-state regressions failed against the original renderer and pass after the fix.
- Full automated suite: **72 tests passed**, including five new regression methods with stale/nullable cache variants, scalar incident dates, cached-question return, and preservation across all six primary destinations.
- Actual Streamlit browser regression: **passed** at 360px, 390px and 1280px, across all nine sections, all primary destinations, question entry/return, retained budgets, dates and edited achievement downloads.
- Connected browser suite: **passed** at 360px and 390px, including profile reuse, encrypted new-session restore and saved earnings reuse.

No merge or deployment is performed by this fix. After review, confirm the original live exception matches, deploy the new commit, restart the Streamlit process if necessary, and verify Policy questions plus Home/Claims/Money/Career/Profile return journeys on the hosted app. Do not describe production as fixed solely from these local results.
