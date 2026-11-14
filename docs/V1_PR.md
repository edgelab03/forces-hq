## Problem and behaviour

The merged application retrieves documents but has no reviewed eligibility decision layer or connected benefit application flow. This branch adds an evidence-gated preliminary assessment engine and a single connected Forces Help to Buy preparation journey. It does not claim a verified production entitlement release.

- Home exposes Claims, Pay, Housing, Pensions and Career; saved earnings/scheme context is shown before modelling controls.
- Assessment rules require version/review dates, a recent document check, exact indexed quotes/locators/hashes and reviewed exception coverage. Questions are asked one at a time, explicit incident dates/meal types are reused, conditional exceptions skip irrelevant questions, and rank/Service/seniority alone cannot establish entitlement.
- The FHTB flow connects assessment, editable purchase estimates, appropriate UK property-tax links, a separate legal-expense check, preparation tasks, progress history and encrypted cross-session restore. Completed benefits are not repeatedly promoted.
- Existing arithmetic, achievements, profile/session functionality remain available. WO1/WO2 profile selections are supported. AFPS 05/EDP calculation logic was absent in the inherited code and has not been invented.

## Required review / not ready to release

Production `policies/rules.json` intentionally has no approved rules. Official-source downloads are blocked by the running environment's outbound policy. Eligibility, scheme monetary limits/repayment terms, exact current JPA process/forms/deadlines, automatic tax calculations and RLE rules are not verified. The UI abstains and labels generic planning estimates. Learning Credits requirements are recorded and implementation is deferred.

Progress persistence is an explicit encrypted-file download/restore, not automatic cloud sync. No official application submission or approval tracking is claimed. See `docs/V1_PRODUCT_PLAN.md` and `policies/README.md` for the release and source-review gates and the proposed (unexecuted) Next.js migration.

## Validation

Final command results are recorded in `docs/V1_VALIDATION.md`. Synthetic policy fixtures test engine mechanics only; no test identifier or invented policy rule is shipped as production authority. Physical Android and hosted deployment verification remain required. No merge, publish or deployment performed.
