# Functional repair audit and delivery evidence

## Root causes observed before editing

The checked-out branch was `feat/v0.9-dashboard-navigation` at `2f7a844`. The previous two dashboard commits existed only locally. A later check found remote main had advanced to `afb20dd781ccf25bd23994d1317520bbaaeebf1a`, adding a dev-container configuration; its app.py and Streamlit minimum were still the old implementation. That unrelated remote change was not overwritten or merged. A read-only `git ls-remote --heads origin` returned `10eeedae080e56f6b1b5875cff8b3317fef7230f` for both main and the remote V0.9 branch. Publishing a Codex cloud snapshot did not push those Git commits or deploy Streamlit. This explains how a GitHub-backed host could keep serving the earlier version; the host's configured branch and entry point cannot be inferred from its URL alone.

The supplied deployment URL is https://forces-hq-3zbdjpxfdhfhuesqubu9q6.streamlit.app/. An actual HTTPS request to it failed at the environment proxy with CONNECT 403. The host's running commit, branch and entry point therefore remain **unverified**. No hosting credentials or deployment configuration exist in the checkout. Nothing was deployed, pushed, merged or published during this repair.

`app.py` previously mixed layout with a `GUIDES` list, a word-overlap/SequenceMatcher ranking function, hardcoded chapter pointers and generic yes/no checks. No PDFs were downloaded, no document corpus was searched, and no policy paragraphs or quotations were retrieved. Meals were absent from the guide list, making unrelated travel suggestions possible. Those generated-looking responses were deterministic text, not an intelligent assistant. The pay table and opportunity descriptions are also static scoped data, not live feeds. No verified step-by-step JPA submission integration exists.

Working capabilities: session input retention, profile validation, budget/savings arithmetic, limited pay comparison, future AFPS 15 accrual arithmetic, official-quote arithmetic, career dates, achievement styles, edited downloads and separate browser sessions. Those capabilities were retained. There was no permanent profile storage, no accounts, no automatic cross-device sync and no full pension/EDP eligibility calculation.

## Repairs implemented

- Removed the section dropdown. Six compact native bottom destinations expose Home, Policy, Claims, Money, Career and Profile. Visible secondary links expose budget/savings, pay/pensions, career dates, achievements and life tools. Existing tools are also available as sidebar buttons. No fixed/sticky positioning or injected navigation JavaScript.
- Home accepts a question and hands its exact text to the same policy experience used by entitlement checks. Related-tool actions retain the question and per-topic clarifications. Example profile values are explicitly labelled until the user applies a profile.
- Replaced the canned guide renderer with extractive document retrieval: official-only HTTPS PDF acquisition, size/redirect limits, PDF text extraction, printed paragraph/heading capture, page anchors, SHA-256 provenance, atomic SQLite FTS5/BM25 indexing, subject expansion and relevance filters. Meals cannot select mileage-only passages. Missing or corrupt documents produce source-unavailable messages, not invented citations. Paragraphs and chapter labels are emitted only when found in document text; otherwise only the PDF page is cited. No generative AI or automatic entitlement decisions are claimed.
- The answer presentation separates answer, unresolved conditions, policy evidence, profile context and next action. Search uses public documents locally; personal questions/profile information are not sent to an external AI service. Scope remains limited to the indexed catalogue, not every JSP or all policy exceptions.
- Linked entitlement-to-policy actions, shared profile context, career dates in profile, profile earnings in pension scenarios, and an explicit calendar-years-to-planned-exit scenario action. Calendar years are not asserted to be qualifying service. Existing budget, savings and pension formulas were preserved. Existing pay source data has not been independently reverified while its source is inaccessible.
- Added explicit encrypted profile download/restore. Structured context, permitted promotion ranks/dates and career dates persist in a password-encrypted user-owned file. Posting locations, free-text notes, questions, appraisal drafts and achievements are excluded. No shared user database or new account system. Restoration validates schema, dates/ranges and authenticated encryption before applying data; visible widgets are synchronised before rendering. Users confirm replacement, can discard prepared encrypted bytes, and control their own files. This is manual persistence, not automatic cloud saving.
- Added a runtime build panel showing branch, commit, entry point, working-tree status and Streamlit version. Hosted identity must still be inspected on that host.

## Tests and practical limits

Automated suite: **45 tests passed** on the final code. Run `.venv/bin/python -m unittest discover -s tests -v`. Existing arithmetic, session, profile and achievement coverage remains; navigation tests were adapted to the removed dropdown. Added meal/mileage isolation, missing/corrupt source abstention, exact source locators, official-host enforcement, partial/failed index refresh preservation, PDF-to-index ingestion, encrypted restore/tamper/schema tests, question handoff, entitlement links, profile propagation and career linkage.

Retrieval fixture texts and the generated PDF are explicitly synthetic test material with invented test-only identifiers. They are confined to temporary test directories. They demonstrate implementation behaviour, **not military policy accuracy or verified live citations**. No synthetic fixture is included in the production index.

Browser commands:

```
APP_URL=http://127.0.0.1:8502 node tests/browser_smoke.cjs
APP_URL=http://127.0.0.1:8502 node tests/browser_connected.cjs
```

Both browser suites passed against a freshly started server on port 8506 (override APP_URL accordingly). The first exercises all nine sections at 360px, 390px and 1280px: touch targets, visible header, two-column cards, card routes, question handoff, navigation availability after scrolling, content clearance, no document overflow, retained budget inputs, reactive date controls, rapid achievement entry and exact edited downloads. The second exercises meals versus mileage, retained clarification answers, profile reuse, encrypted download and restore in a new browser context, pension earnings reuse and persisted career dates at both mobile widths. Dependency integrity check (`python -m pip check`) passed. Budget/savings and AFPS 15 calculation blocks were compared with the prior commit and remained unchanged; existing arithmetic regression cases passed. Local screenshots are in `/tmp/forces-hq-phase1` and `/tmp/forces-connected-360.png`, `/tmp/forces-connected-390.png`.

Physical Android remains necessary for keyboard/Chrome toolbar resizing, focus scrolling, touch usability, text scaling and session lifecycle. The Streamlit app still reruns on interaction and is not an offline/native application. Automatic secure cross-device saving would require authenticated identity and protected storage; a mobile web frontend with a separate API would be a realistic later architecture if native interaction or stronger persistence is required. This task does not claim that migration or a general conversational reasoning model is implemented.

## Blockers and required configuration

Actual requests to the GOV.UK JSP 752 landing page, official assets host and deployed app were denied by this environment's proxy. The `scripts/index_policies.py --source 'JSP 752'` run reported `state: unavailable`, zero official documents. Consequently **live policy retrieval and the deployed app remain unverified**. Retrieval mechanics, source failure behaviour and local application journeys were tested independently.

Draft network additions were saved for `www.gov.uk`, `www.publishing.service.gov.uk`, `assets.publishing.service.gov.uk`, `www.legislation.gov.uk`, the exact deployed `.streamlit.app` host and `share.streamlit.io`; existing package-manager presets were retained. Draft saving did not apply these rules or publish anything. Review/save access in environment settings, verify a fresh HTTPS connection, then run:

```
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/index_policies.py
.venv/bin/python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
```

The index defaults to `policy_data/`; `FORCES_POLICY_DIR` can select a retained public-document cache. Generated PDFs, databases and manifests are ignored by Git; they must be created on the target host. The script exits nonzero for unavailable/partial refreshes and preserves usable previous indexed sources on failed/limited refreshes. Review manifests and full source editions; retrieval does not establish current legal applicability. Re-run indexing when publications change. Automatic refresh/scheduling is not configured.

For a later authorised deployment, make the tested commit available on the host's configured Git branch, confirm `app.py` as entry point and install the updated requirements (Streamlit 1.67+, pypdf and cryptography). Inspect the hosted build panel and verify actual source retrieval and core journeys there. No release, source-currentness or deployment success is asserted by local tests.
