# Forces HQ

Independent educational military career, money and public-policy application. Not an official MOD service. Use fictional, non-identifying information only.

## Run locally

Python 3.12 is the development baseline. Use the existing checkout:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/index_policies.py
.venv/bin/python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
```

The public-document indexer needs verified HTTPS access to `www.gov.uk` and official PDF hosts `assets.publishing.service.gov.uk` / `www.publishing.service.gov.uk`. It follows links from the catalogue's publication pages, extracts PDF text and records page/paragraph locations, retrieval times and file hashes. `policy_data/` is a generated local public-document cache, excluded from Git. `FORCES_POLICY_DIR` can override its location. Index refresh is explicit; configure refresh on the deployment host and check the resulting manifest. Failed source downloads do not create substitute policy text.

If no relevant indexed passage is available, the app says **Source unavailable** and does not supply a fabricated paragraph or quotation. Document search uses SQLite full-text BM25, subject expansion and guided clarifications. It is not generative AI or a verified eligibility engine. Public coverage is limited to downloaded catalogue documents; inaccessible reporting instructions and other unsupported questions require authorised advice.

## Connected workflow

Home accepts a natural-language question. Policy shows clarification questions, indexed evidence, profile context and next actions. Claims links schemes directly into policy checks. Money contains budget/savings and pay/pension scenarios. Career contains milestones, achievements and life tools. Profile retains the existing validated entry workflow. Six compact bottom destinations remain available throughout; the old section dropdown is removed.

The profile is shared within the current session. To retain structured settings and career dates between sessions, use **Save or restore an encrypted profile**. Download the `.fhq` file and keep its passphrase separately. Restore is explicit and validated. There is no account, automatic cloud sync or shared user database; losing the file or passphrase has no recovery service. Posting locations, free-text notes, questions and achievement drafts are excluded from this backup. Existing edited achievement downloads remain available independently. Never enter classified/operational information, service identifiers, official appraisal text or identifiable family details. Never commit `.streamlit/secrets.toml`.

Calculations remain limited: budget/savings illustrations, the existing OR7 pay comparison, future AFPS 15 accrual and official-quote arithmetic. Rank alone does not establish pensionable earnings; dates alone do not establish qualifying service. No general pay coverage, EDP calculation, entitlement award or JPA submission is provided. Existing pay-source data still needs independent source review.

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
APP_URL=http://127.0.0.1:8502 CHROMIUM_PATH=/usr/bin/chromium node tests/browser_smoke.cjs
APP_URL=http://127.0.0.1:8502 CHROMIUM_PATH=/usr/bin/chromium node tests/browser_connected.cjs
```

Start Streamlit on port 8502 for those browser commands. Node, Playwright and Chromium are browser-test prerequisites. Tests cover all nine existing sections, input retention, arithmetic, achievements, meal/mileage separation, missing sources, PDF ingestion/ranking, linked policy checks and encrypted new-session restore. Synthetic policy test fixtures validate code behaviour, not real military policy. Browser widths: 360px, 390px and desktop; physical Android checks remain necessary.

Read [REPAIR_AUDIT.md](REPAIR_AUDIT.md) for root causes, tested scope, source/network blockers and deployment requirements. The sidebar build panel identifies the **running process**; publishing a cloud development environment neither pushes Git commits nor deploys a Streamlit host.

## V1 guided benefits work

The V1 product scope, source/release gates and unexecuted frontend migration proposal are in [docs/V1_PRODUCT_PLAN.md](docs/V1_PRODUCT_PLAN.md). The branch adds source-gated decision rules and a connected FHTB preparation/checklist flow; it does not claim verified scheme eligibility while production rules are unapproved. Benefit progress and budget assumptions can be included in the explicit encrypted profile backup. Validate rules with `python scripts/validate_rules.py`; the current missing-rule check intentionally fails. Learning Credits remains deferred.

New exports can include V1 benefit progress and budget assumptions; older exports still restore with an empty benefit journey. Restore in the V1 app to recover that progress—older deployed code does not understand the new optional benefit payload.
