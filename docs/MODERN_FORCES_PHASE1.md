# Modern Forces mobile UI — Phase 1

Base: `697a217` on main, including the merged Policy TypeError hotfix. Branch: `feat/modern-forces-mobile-ui`.

## Screens and components

- Home: compact original F/forest/gold wordmark, “Your service. Simplified.” tagline, profile icon, confirmed-profile greeting, short explanation, forest Ask panel, white draft field, disabled mic icon and working Ask arrow. Four full-surface native cards form a 2×2 grid: Your pay, Housing, Pension, Learning.
- Shared frame: light ivory/white theme, forest primary actions, mint selection states, soft blue next-step surface, native outline Material icons, 20px mobile margins, 18–20px radii, full-width controls and accessible focus outlines. Inter is used when installed with a system sans-serif fallback; no external font dependency is introduced. Branding is static SVG/typography, not military clip art.
- Navigation: five native icon buttons in Streamlit's supported bottom container, with visible active state and safe-area padding. No main-navigation radio widget, dropdown, horizontal text-link list or custom fixed positioning. Streamlit's default extra bottom padding is reduced with container padding, not a replacement positioning system.
- Recommendations: reuse the existing evidence-gated benefit result. No new eligibility rule or fictitious benefit. A saved FHTB goal gets one resume card rather than duplicated recommendation/progress actions. Otherwise an actual upcoming saved milestone can be shown. Empty placeholder progress cards are omitted.
- Learning: maps to existing course/qualification milestone planning, clearly labelled Learning & development. Learning Credits eligibility remains unimplemented; no new policy content or entitlement is added.

## Route mapping

| Action | Existing destination |
| --- | --- |
| Home | Dashboard |
| Ask | Policy / Ask Forces HQ |
| Money / Your pay | Existing money overview, with budget and pay/pension actions |
| Explore | Benefits and existing career, achievement and life tools |
| Me / profile icon | Existing military profile and encrypted saving |
| Housing | Existing FHTB guide, resuming saved step |
| Pension | Existing pay/pension modelling screen |
| Learning | Existing career course/qualification planning |

`ui_navigation.py` maintains a bounded history of page/journey/presentation identifiers, not copies of profile or financial inputs. The in-app Back control restores the previous route and its context. Existing page identifiers and input keys remain stable, preserving the V0.8 retention mechanism and later saved benefits. Home remains the root dashboard without an extra Back row.

## Features preserved and scope check

A comparison with main confirmed **byte-for-byte unchanged screen bodies** for Profile, budget/savings, Policy Ask, achievements and pay/pension. Core policy/decision/source modules, profile backup, benefit rules/calculators and session-input retention have no changes. Career gains a presentation-only learning heading/caption; its fields, records and calculations remain intact. The inherited production-rule/source limitations remain in force; this UI update makes no new entitlement or source-accuracy claims.

## Verification

- Full automated suite: **77 tests passed**. The final one-line dashboard copy was subsequently covered by the five-width Modern Forces browser suite. Includes the retained-state Policy TypeError regressions and new five-tab/history/draft/card tests.
- Existing browser regression suite: passed at 360px, 390px and 1280px, including all nine tools, budgets, dates, achievements and exact edited downloads.
- Existing connected-profile and V1 guided suites: passed at 360px and 390px, including profile reuse, encrypted new-session restore, FHTB checklist/budget retention and completed-benefit suppression.
- New Modern Forces suite: tests **360px, 390px, 412px, 768px and 1280px**. Asserts the ivory background, two-column grid, five native icon buttons, ≥44px touch targets, no nav-label clipping, no document overflow, active tab, all card destinations, disabled microphone, appropriate in-app Back, question/guide retention, footer clearance and question input clearance in a resized 500px-high viewport.
- UI tests wait for actual Streamlit render completion. Native menu tests can reopen a menu interrupted by a rerun and always assert the selected value; no functional assertions are disabled.

Commands (start the app on the chosen APP_URL port):

```
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
APP_URL=http://127.0.0.1:8531 node tests/browser_smoke.cjs
APP_URL=http://127.0.0.1:8531 node tests/browser_connected.cjs
APP_URL=http://127.0.0.1:8531 node tests/browser_v1.cjs
APP_URL=http://127.0.0.1:8531 node tests/browser_modern.cjs
```

Screenshots: `/tmp/modern-forces/home-360.png`, `home-390.png`, `home-412.png`, `home-768.png`, `home-1280.png`. These are local review artifacts, not deployed previews.

## Streamlit limits and next stage

Native Streamlit text inputs have no focus/click routing callback. The home input therefore opens Ask on **Enter, committed text/blur or the explicit arrow**, preserving the typed draft. Focus alone keeps the user in the home field so typing works. No browser-event interception or fake editable launcher is added. The microphone is disabled and labelled unavailable; there is no pretend speech recognition.

Back is an explicit in-app action. Android hardware/browser Back is not intercepted and can leave the application. Viewport resizing tests approximate reduced keyboard space; they do not verify an Android keyboard. Real Android tests remain required for Chrome toolbar collapse, keyboard resizing, focus scrolling, safe areas, enlarged text, touch use, external-document return and session recovery. Automated checks do not establish full WCAG conformance.

The existing session lifecycle and explicit encrypted-file saving remain unchanged; this is not automatic cloud sync. Streamlit still reruns controls, and its button-content markup needs visual retesting on upgrades. CSS is scoped to component keys/data attributes and presentation; no DOM event handlers or generated hash selectors are used.

If immediate focus-to-route transitions, shareable routes, browser Back behaviour and durable client drafts are required, a **targeted next phase** should put the dashboard/navigation and Ask shell in Next.js while retaining Python decision/calculation services behind a versioned API. Introduce authenticated progress storage only after privacy/security review. Migrate one shell/journey at a time with parity tests and rollback. That migration is a proposal, not part of Phase 1.

## Release discipline

No automatic merge, environment publication or deployment. Review the branch and screenshots, then deploy the correct commit with `.streamlit/config.toml`, `modern_ui.css`, `modern_ui.py` and `ui_navigation.py` included. Restart Streamlit as needed for the theme configuration. Verify the hosted build panel and mobile appearance independently before stating the live app updated. PR creation may require enabling the GitHub API in this environment's network settings.

## Final acceptance outcome

All four browser suites passed: legacy nine-section regression (360/390/1280px), connected profile/export/restore (360/390px), V1 guided FHTB journeys (360/390px), and Modern Forces layout/navigation (360/390/412/768/1280px). Dependency integrity and Git whitespace checks passed. No tests were skipped to obtain these results. Hosted deployment and physical Android checks are not included in those passes.
