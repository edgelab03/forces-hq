# Modern Forces Phase 1.1

## Recovery and scope

Recovered GitHub main at `6d8136e` (merged Phase 1 PR #6), rather than continuing the stale local `work` checkout at `10eeeda`. GitHub branch and pull-request inspection found the Phase 1 implementation, guided-benefits work and policy state fix already committed. No separate Phase 1.1 branch was available at recovery. Continue on `feat/modern-forces-phase-1-1`; do not merge or deploy automatically.

## Stage 1: light theme and mobile actions

- Pale green Ask panel on the existing ivory page, forest text and a forest submit control with white icon.
- Long button/source labels wrap; home cards and five navigation destinations keep their existing layout.
- Previous/Continue journey actions share a wrapping row with full-width touch targets.
- Native chat surfaces use white cards and the existing green/ivory palette.

First checkpoint: `ef0862c`. The 77-test recovered suite passed after installing the repository's declared dependencies. Existing responsive checks passed at 360, 390, 412, 768 and 1280px.

## Stage 2: conversational claim checks

Ask offers meal, mileage and home-buying prompts. A current check shows the user's question, explicitly recognised date/meal, confirmed condition answers and the current assessment in native conversation messages. The transcript is rebuilt from the existing assessment facts, avoiding a second store that could disagree with the decision engine. Only the next necessary condition is asked. Navigation keeps the question and answers.

“Start a new claim check” clears the current meal/mileage check and Home draft, leaving other topics, the profile and saved benefit progress intact. The existing answer-change control remains available inside evidence details.

No production policy rule, eligibility inference, financial calculation, encrypted backup format or official application integration changes. Without reviewed current policy, the conversation reports that it cannot verify entitlement and links to evidence/support; it does not invent an interview or approval. This remains deterministic guidance, not generative chat.

## Validation

Automated claim regressions cover missing-source abstention, prompt/navigation retention, fresh-check isolation, and a complete one-question-at-a-time interaction using an explicitly synthetic reviewed rule fixture. The fixture is never loaded as production policy.

The Modern Forces browser suite now covers 320, 360, 390, 412, 768 and 1280px, including pale-green/ivory colours, navigation and cards, conversation messages, missing-source behaviour, fresh-check reset, purchase-budget editing, same-row journey controls, overflow and reduced-height input clearance. Screenshots are local review artifacts under `/tmp/modern-forces/`.

Final validation:

- Full Python suite: **80 tests passed**. The three conversation tests also passed after the final avatar styling change.
- Modern Forces browser suite: **320, 360, 390, 412, 768 and 1280px**. Includes one-line navigation labels after visual review identified and corrected Explore wrapping at 320px.
- Existing application browser regression: **360, 390 and 1280px**, all nine tools, retained inputs, arithmetic and edited downloads.
- Connected-profile browser regression: **360 and 390px**, including encrypted new-session restore, salary reuse and career persistence.
- V1 guided-benefit browser regression: **360 and 390px**, including purchase arithmetic, policy abstention, separate legal-expense routing, encrypted checklist restore and completed-journey suppression.
- Dependency integrity (`pip check`) and Git whitespace checks passed.

Browser checks now wait for the new-claim prompt and newly added milestone to render before testing or exporting them. The V1 download wait and click are paired, with a failure screenshot retained if either fails. No functional assertions were removed. The first browser runs encountered stale imported modules and intermittent render/download timing failures; final acceptance used fresh server processes and the explicit render waits above.

Physical Android keyboard, hardware Back and safe-area behaviour still require device testing as described in Phase 1. No hosted deployment is claimed.

## Environment recovery

Initial Git fetch failed because the sandbox proxy was unreachable; a network-enabled retry succeeded. The retained virtual environment lacked `cryptography` and `pypdf`; installing `requirements.txt` restored the recovered application's dependencies. Starting the local test server and Chromium required execution outside the default sandbox. These were environment failures, not application regressions.
