# Forces HQ V0.9.1

An independent educational **demonstration** app for exploring British Armed Forces career planning, money and policy. Not affiliated with the Ministry of Defence.

## Dashboard and navigation

Home has a compact welcome card, four two-column shortcuts (Policy, Claims, Money and Career), and an **Ask a military question** entry to the existing policy finder. Home, Explore, Money and Profile remain available in Streamlit's native bottom container. The full section list is in the optional sidebar; Explore and Money also expose their secondary tools. Streamlit 1.67 or later is required for supported bottom placement.

No tool calculations, policy references, budget inputs or profile onboarding have changed. Data remains within the current session. See [V0.9.1_REVIEW.md](V0.9.1_REVIEW.md) for validation scope and real Android checks.

## Changes in Phase 1

- The original **Go to section** selector includes all nine sections; V0.9.1 moves it into the optional sidebar and adds compact bottom navigation. Navigation controls remain in sync.
- Budget and savings inputs, profile drafts, policy searches and answers, filters, milestone drafts, achievement drafts and pension scenarios survive section changes **within the same browser session**.
- Entry panels update their draft fields immediately. Explicit buttons still apply the linked profile, add records and calculate the pension scenario. This avoids losing an unsubmitted form when navigating away.
- Optional profile dates enable immediately when ticked, use day/month/year formatting, and start blank. The app asks for missing dates, rejects birth dates on/after enlistment, and prevents selecting both named pension schemes and “Not sure”.
- Each achievement output style keeps its own edits. Downloads contain the edited text. Unedited drafts update when examples are added; edited drafts are preserved until **Regenerate this draft from practice examples** is selected.
- The last calculated future-accrual scenario stays visible when returning to the pension page. Changed inputs are labelled until recalculated. Transferring a comparison pay figure updates the scenario without changing the saved profile.
- A consistent dark theme, larger touch targets, readable inputs, wrapping results, visible keyboard focus and stacked phone layouts improve mobile use, including Android-sized screens.

Existing calculations, pay-table entries, policy references and entitlement content are retained. This phase adds no JSP references, pension rates or entitlements, and does not establish that existing sources have been independently verified.

## Local development

Use Python 3.12, with a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Keep `app.py`, `session_inputs.py`, `requirements.txt` and `.streamlit/config.toml` together in the checkout. The theme file makes inputs and surrounding panels use the same colours. Never commit `.streamlit/secrets.toml`.

## Regression checks

The automated application suite uses Streamlit's testing tools and Python's standard library, with no separate test dependency:

```sh
python -m unittest discover -s tests -v
python -m pip check
```

It exercises all nine sections, navigation state, retained inputs, optional dates and profile validation, adding/removing milestones, achievement styles and edits, session isolation, pay transfer, and existing savings/pension arithmetic using fictional test inputs. Passing arithmetic tests does not validate military eligibility or pension policy.

For browser checks, install Node.js, Playwright and Chromium. With `playwright` available to Node's module resolver, run a local server and then the script in another terminal:

```sh
python -m streamlit run app.py --server.headless=true --server.port=8502 --browser.gatherUsageStats=false
```

```sh
APP_URL=http://127.0.0.1:8502 CHROMIUM_PATH=/usr/bin/chromium node tests/browser_smoke.cjs
```

The browser script exercises 360px and 390px Android-style viewports plus a 1280px desktop viewport. It checks every section, navigation while scrolled, retained inputs, reactive date controls and the actual edited download. Screenshots go to `/tmp/forces-hq-phase1` by default; override `ARTIFACT_DIR` if needed. Emulation does not replace testing on a physical Android device.

## Existing features

- Linked demo military profile, self-reported scheme history and dated promotion timeline.
- Dashboard guidance and an opportunities explorer.
- Curated policy-topic matching, travel questions and official-source links.
- Custom career, MPAR, SJAR and OJAR milestones, with manual add/remove controls.
- Achievement log and three structured drafting styles; no generative AI.
- Budget, savings and inflation illustrations.
- Limited existing OR7 pay comparison, future AFPS 15 accrual illustration, and Added Pension quote/demo arithmetic.
- Life-planning links and official pension-calculator signposting.

## Session data and limitations

**Session retention is not permanent saving.** No account, database, browser local storage or cross-device synchronisation is introduced. Refreshing, losing the session, restarting the server or opening another session may reset data. Use fictional, non-identifying information only.

Do not enter service identifiers, real posting details, official appraisal text, personnel records, restricted material or identifiable family/financial information. Downloaded practice notes are local files and are outside the app's session lifecycle.

This remains a proof of concept, not a policy eligibility engine, financial advice, an official pension calculator or a secure MOD system. It neither accesses JPA nor submits claims. Existing policy citations, pay sources, JPA guidance gaps and broader Service/rank coverage still need the separate content and specialist review identified in the V0.8 audit. Secure long-term saving, accounts and reminders remain future work.

Phase 1 is intended for pull-request review; it does not merge or deploy the application.
