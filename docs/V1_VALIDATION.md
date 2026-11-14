# V1 validation scope

Base: `ce590f733475100b83957f51ebf7ae247a76eafc` (merged V0.9 functional repair plus existing dev-container configuration). Feature branch: `feat/v1-guided-benefits`.

Commands:

```
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
APP_URL=http://127.0.0.1:8512 node tests/browser_smoke.cjs
APP_URL=http://127.0.0.1:8512 node tests/browser_connected.cjs
APP_URL=http://127.0.0.1:8512 node tests/browser_v1.cjs
.venv/bin/python scripts/validate_rules.py
```

The browser runs use a freshly started Streamlit process and Chromium with 360px/390px mobile emulation; the regression suite also uses 1280px desktop. They exercise all nine existing pages, five dashboard tiles, persistent navigation, no document overflow, touch targets, state retention, profile validation, pension salary reuse, achievements and exact edited downloads. The V1 suite walks Private and WO1 meal questions, mileage source-gated abstention, housing handoff/return, all five FHTB planning steps, generic purchase arithmetic, devolved tax routing, separate legal-expense handoff, checklist export/restore in another browser session and completed-benefit suppression.

Unit/AppTest coverage additionally uses explicitly synthetic reviewed rule fixtures to exercise preliminary eligible/ineligible/further-information statuses, exact hash/quotation/locator checking, expiry/staleness, date applicability, conditional exceptions, one necessary question at a time, changed-answer reset, same-circumstances rank parity and rejected seniority-only rules. Those fixtures are temporary test data, not primary-source policy evidence. Production decisions remain unable to verify while the registry has no approved rules.

Source access: actual requests to the official FHTB guidance and GitHub GraphQL API returned proxy 403. Environment status remains revision 1 with no applied custom allowlist, although a review draft contains official-source and API domains. No source terms were invented to bypass this blocker. External URL target checks in browser tests establish correct href routing, not successful remote responses or document currency. Live source-link verification is blocked.

No secure auto-sync, AFPS 05/EDP calculator, automatic current property-tax calculator, verified JPA submission flow, Learning Credits implementation or production deployment is claimed. These limitations are recorded in the product plan. Physical Android keyboard/toolbar behaviour, text scaling, touch use, external-document return and disconnect/recovery remain untested.

Final outcomes are appended after acceptance checks.

## Final local outcomes

- Full automated suite: **67 tests passed**. This includes the inherited arithmetic, profile, navigation and achievement coverage plus the new decision and guided-journey cases.
- Dependency check: **passed**, no broken requirements.
- Browser regression suite: **passed** at 360px, 390px and 1280px, covering all nine existing pages and their retained inputs/downloads.
- Connected profile suite: **passed** at 360px and 390px, including saved earnings reuse and encrypted new-session restore.
- V1 guided suite: **passed** at 360px and 390px, including both user personas, meal/mileage abstention, FHTB handoff/return, purchase arithmetic, nation-specific tax hrefs, separate legal-expense check, all preparation steps, encrypted checklist restore and completed-benefit suppression.
- AST comparison confirmed the existing AFPS 15 accrual loop and pay-table data are unchanged; calculation fixtures passed. No AFPS 05 or EDP engine was present to validate.
- The rule validation command **intentionally exits 1**: FHTB, meals and mileage lack approved current primary-source rule packs. `rule_gate_passed` and `release_ready` are false. This is a release blocker, not a passing policy-accuracy check.

Browser tests target the actual local Streamlit app. Short-lived duplicate controls during Streamlit reruns and virtualised rank-option menus required waiting for the settled page and navigating the real menu. Saved persona values are asserted after application; no test removes the persona or eligibility assertions to bypass a failure.

Physical Android and independently verified hosted deployment remain outstanding. The local screenshot `/tmp/forces-v1-home.png` shows the current mobile home; guided/completed snapshots are `/tmp/forces-v1-completed-360.png` and `/tmp/forces-v1-completed-390.png`. These are ephemeral local artifacts.
