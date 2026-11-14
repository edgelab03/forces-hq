# Stage A connected foundation — validation

Branch: `feat/forces-hq-connected-foundation`, based on main `2137a45`. This is **Stage A only**. The approved visual system, colour-mode behaviour, existing Python calculations, production policy rules, Streamlit configuration and root regression tests are unchanged.

## Implemented architecture

The protected Next.js application calls a same-origin, allowlisted server gateway. The gateway uses a separate server-only credential to call stateless FastAPI. Real profile operations call the existing Python `profile_backup.validate/save/load` and `app_context.linked_milestones`. No financial formula was copied into JavaScript.

Me edits service/rank, service type, relevant dates/circumstances, scheme memberships, earnings attestation and promotion history. Canonical API results update Home. There is no fictional default person, monthly income or savings. Confirmed profiles and drafts are memory-only: navigation preserves them, reload clears them, and explicit encrypted files provide user-controlled persistence. The existing backup format preserves compatible imported career events and FHTB state without exposing free-text/private identifiers.

## Passing checks

| Check | Result | What it establishes |
| --- | --- | --- |
| Existing Python suite | **80 passed** | Existing Streamlit functionality, financial arithmetic, retained inputs, evidence gates, backups and journeys remain intact |
| New API integration suite | **16 passed** | Typed profile boundaries, shared validation/crypto compatibility, auth, limits, redacted errors, no profile store, milestones and unexpected-exception privacy boundary |
| Connected + existing frontend browser suites | **27 passed** at **360, 390, 412px** | Real Next.js→FastAPI profile operations; contextual Home; file export and wrong-password/correct-password restore in a new context; memory-only reload behaviour; failed-update preservation; auth/origin/path boundaries; navigation and keyboard-layout regression checks |
| `npm run typecheck` | Passed | Frontend and gateway TypeScript types |
| `npm run build` | Passed | Production Next.js build, including API route and authentication Proxy |
| `pip check`, `git diff --check` | Passed | Dependency integrity and whitespace checks |
| Client asset inspection | Passed | API token/private access variable names and synthetic service token absent from built public JavaScript |
| Existing root application diff check | Passed | Root Python application/modules, rules, Streamlit config, requirements and original tests unchanged |

All normal success workflows hit the actual local Python service. The explicit outage test aborts the update request to verify that a failed request cannot replace confirmed profile state; it does not mock a successful connection. Tests use synthetic profiles and credentials only. The first browser pass identified label/select matching and framework-announcer selector ambiguities; final checks use explicit accessible labels and scoped alerts. No successful-response or preservation assertion was removed to obtain a pass.

## Actual rendered captures

These images show **synthetic test entries submitted to the real API**, not built-in application defaults. Home/Me remain in the approved Modern Forces visual language. The profile and confirmed Home renders were visually reviewed alongside functional testing.

| Mobile viewport | Confirmed Home | Real profile editor |
| --- | --- | --- |
| 360 × 800 | [Home](screenshots/connected/home-360.png) | [Me](screenshots/connected/profile-360.png) |
| 390 × 844 | [Home](screenshots/connected/home-390.png) | [Me](screenshots/connected/profile-390.png) |
| 412 × 915 | [Home](screenshots/connected/home-412.png) | [Me](screenshots/connected/profile-412.png) |

Additional onboarding, navigation and explicitly labelled Ask-demo captures are under `screenshots/connected/navigation/`. The older prototype images remain historical design artifacts. No colour-mode investigation or redesign is included.

## Not yet connected or verified

- Money/pay/pension outputs and responsive financial charts: Stage B. Home can display **entered, user-attested annual earnings**, never a calculated take-home amount.
- Meal/mileage policy conversation, reviewed evidence and eligibility assessment: Stage C. Ask remains a clearly marked scripted demonstration and is not using the live policy engine.
- Guided FHTB/career/learning interface: Stage D. Backups preserve existing data; the new frontend does not yet edit or assess those journeys.
- Learning Credits eligibility, AFPS 05 reconstruction, EDP calculation, verified production policy rules, automatic property-tax calculations and live JPA submission are not existing capabilities; see the inventory.
- Independent backend hosting, Vercel environment configuration and physical Android/hosted-service acceptance are pending. Local processes do not establish Vercel connectivity.
- Shared Basic private-preview access is implemented, **not** individual production accounts/OIDC, server-side user persistence, automatic sync, or a full security/accessibility audit. Hosting rate limits and request-log privacy must be configured before handling hosted personal data.
- The proposed container recipe has not been built/deployed as part of this task. No merge, backend deployment or Vercel deployment was performed.

See [the deployment guide](../../docs/CONNECTED_DEPLOYMENT.md) for TLS, all required server-only variables, local setup, proposed hosting, authentication release gates and rollback steps; see [the data contract](../../docs/CONNECTED_API_CONTRACT.md) for the exact endpoint scope.
