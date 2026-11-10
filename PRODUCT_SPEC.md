# Forces HQ — Product Specification 1.0
**Status:** Proposed product baseline for review  
**Date:** 10 November 2026  
**Repository:** `edgelab03/forces-hq`  
**Owner's direction:** Complete British military life and career companion, delivered in controlled stages.

## 1. Mission and positioning
Forces HQ is an **independent, mobile-first, non-MOD-affiliated** guidance companion for serving British Armed Forces personnel. Help users understand their circumstances, find relevant public military policy, evaluate potential entitlements, take practical administrative actions, and plan their career, pay, pension and family life.

**Core sequence:** User circumstances → verified relevant source and decision rules → clear, actionable next step.

### Success outcomes
- Find evidence-backed guidance for a supported administrative scenario without knowing a JSP number.
- Understand a potential entitlement and all material eligibility conditions or uncertainty.
- Follow practical instructions to prepare a claim, without pretending to submit it.
- Compare supported pay and pension scenarios with visible assumptions and limitations.
- Track permitted career and life milestones on a usable mobile interface.

## 2. Scope and boundaries
**Initial audience:** serving Army, Royal Navy, Royal Marines and RAF personnel; begin with explicitly supported subsets rather than claiming universal coverage. All written outputs in UK English.

**In scope eventually:** dashboard, profile, verified policy finder, guided JPA/allowances, pay/pension illustrations, career development, military-life checklists, privacy/settings.

**Out of scope for initial release:** connection to JPA/MOD systems; submitting or approving claims; access to restricted policy; handling classified or OFFICIAL-SENSITIVE material; processing operational/CP details; formal entitlement determinations; official pensions statements; sensitive personnel reporting; monetisation or native Android app.

**Trust model:** AI may interpret plain-language questions and draft explanations, but must not serve as the source of entitlement truth. Verified documents and reviewed, deterministic decision rules determine conclusions. Where rules or circumstances are insufficient, answer **unable to determine**, explain why, and refer to an authorised source.

## 3. Existing baseline (as inspected 10 Nov 2026)
- Main branch: Streamlit demonstration app with a demo profile, nine sections, curated links/topic matching, milestones, achievement drafts, savings/budget tools, narrow OR7 pay comparison and limited AFPS 15 illustrations.
- `feat/v0.8-phase1-navigation`: development branch reported improved sticky navigation, within-session input retention, date validation and regression tests. This is **not yet a verified merged/live release**.
- No permanent profile storage, user accounts, trusted entitlement engine, comprehensive Service/rank pension coverage or JPA connection.
- Do not imply existing policy/pay/pension references are verified merely because regression tests pass.

## 4. Functional requirements and acceptance criteria
### FHQ-01 — Dashboard
**Requirements:** a summary of the user's selected profile, supported opportunities to check, upcoming milestones, saved actions (when approved), and quick access to every major section.
**Acceptance:** navigation accessible from every page; relevant content updates on profile change; no unsupported entitlement shown as confirmed; mobile presentation and accessible keyboard navigation.

### FHQ-02 — Military profile
**Requirements:** capture Service, rank, rank/pay level where supported, enlistment and promotion history, role, declared pension schemes, planned exit and optional non-sensitive context. Household details only after privacy controls are approved.
**Acceptance:** validate date ordering and mutually incompatible choices; clearly show unknown/unverified data; fields are re-used consistently; users can edit/clear; unsupported Services/ranks are labelled rather than guessed.

### FHQ-03 — Policy intelligence
**Requirements:** searchable catalogued PUBLIC policies with version, effective date, verified section/paragraph, applicability, exceptions, last-reviewed date and source link; plain-language explanation.
**Acceptance:** every substantive policy conclusion cites a traceable, checked source; exact paragraph text and numbering match the source; revision status tracked; unavailable or conflicting sources cause safe abstention/escalation, never fabricated citations. Policy update does not require UI code changes.

### FHQ-04 — JPA & entitlements assistant
**Requirements:** guided question flow for selected duty travel, subsistence, HTD, GYH, relocation, accommodation, family/education and other explicitly supported cases. Present eligibility status (potentially eligible / not indicated / cannot determine), critical conditions, exclusions, evidence needed, verified navigation steps and factual editable claim justification where appropriate.
**Acceptance:** each supported scenario has an approved decision table and tests for qualifying, disqualifying, missing-data and exception cases; no unsupported definitive approval; never claims to have submitted anything; 220-character template only where field limit is verified or user specifies it; do not advise false claims or altered receipts.

### FHQ-05 — Pay and pensions
**Requirements:** dated source-controlled rank/pay tables; salary comparisons; declared pension scheme histories; AFPS 75/05/15 and EDP only as coverage is verified; scenario comparisons and official calculator links.
**Acceptance:** outputs identify source, effective date, scheme, pensionable-pay assumption, calculation inputs, rounding and exclusions; mixed-scheme histories handled explicitly; benchmark fixtures reconcile within declared tolerance; if insufficiently supported, do not calculate an apparently precise entitlement.

### FHQ-06 — Career development
**Requirements:** qualification/milestone tracker; MPAR/SJAR/OJAR preparation guidance; achievement log, evidence-based drafts; exit and resettlement checklist.
**Acceptance:** create/edit/remove/export permitted non-sensitive entries; no fabricated achievements; draft style and manual edits retained within stated storage limits; not represented as an official reporting system.

### FHQ-07 — Military life
**Requirements:** checklists and official links for assignments, accommodation, education/CEA, family support, childcare, leave, relocation and resettlement.
**Acceptance:** relevant support paths match the provided circumstances; sources and eligibility caveats are visible; being a parent or posted does not alone assert entitlement.

### FHQ-08 — Trust, privacy and settings
**Requirements:** independent/non-MOD label, source version and limitations, data controls, feedback and accessible preferences.
**Acceptance:** data retention and transmission are clearly disclosed; no genuine military identifiers/operational information solicited for the demonstration; before persistent storage, a documented data protection, security, deletion and incident-response review is mandatory.

## 5. Data and source design
Separate the application into:
1. **Presentation:** Streamlit dashboard/forms/navigation, no embedded entitlement policy logic.
2. **Application services:** validation, profile service, guided workflows and document/claim formatting.
3. **Policy catalogue:** immutable source ID, publisher, public URL, document identifier/edition, effective date, retrieved/reviewed dates, verified passage locator, conditions, exceptions, status (verified/needs-review/superseded/unsupported).
4. **Rules and calculators:** independently testable versioned code with test fixtures and audit trail.
5. **User data:** currently session-only fictional data; future approved persistence is a distinct gated project.

Policy engine must explain exactly which rule and user answer affected the outcome; no black-box decision alone.

## 6. Non-functional and release acceptance
- **Reliability:** 100% agreed automated regression suite passes, zero open release-blocking defects.
- **Mobile:** 360px, 390px and desktop viewport tests plus a real Android test; no horizontal overflow, tap targets and keyboard/focus accessible.
- **Accessibility:** target WCAG 2.2 AA for public interface; verify with automated and manual checks.
- **Source fidelity:** 100% supported policy conclusions have independently checked authority/version/locator; unsupported questions safely abstain.
- **Calculations:** 100% of approved reference cases pass within explicit rounding tolerances.
- **Performance target:** interactive primary page within 3 seconds in specified test environment, excluding external retrieval; measure and record rather than assume.
- **Usability beta target:** >=90% independent task completion across agreed test scenarios with zero critical policy errors.
- **Privacy:** no real persistent user data until security/privacy design is approved.
- **Change control:** small scoped branch, linked requirement IDs, tests and PR review, explicit rollback, no direct production deploy.

## 7. Delivery stages and gates
### Stage 0 — Baseline/specification
Deliver this spec, requirements/test traceability, current state inventory and list of open questions. Gate: accepted baseline; no app code modified as part of the documentation task.

### Stage 1 — V0.8 reliable foundations
Review existing Phase 1 branch, execute existing tests, test actual Android, resolve verified defects, define modular boundaries. Gate: all nine sections and declared session functions work; no regressions; reviewed PR and rollback plan.

### Stage 2 — V0.9 verified policy/JPA pilot
Build structured source catalogue and deterministic workflows for a **small, reviewed set** of common scenarios. Initial candidate list: missed evening meal during duty; authorised travel/parking; privately owned vehicle mileage; overnight subsistence; HTD; GYH; relocation expenses; SFA/SLA question; CEA referral; service separation/absence allowances. These are **research candidates**, not promised verified coverage.
Gate: for each chosen case, documented eligibility matrix, citation validation, exception/missing-data tests, practical guidance where verified, policy reviewer sign-off.

### Stage 3 — V1.0 career and financial companion
Expand profiles, dated pay tables, supported pension/EDP calculations, milestones, dashboard relevance. Gate: published coverage matrix and independently benchmarked calculations; unknown inputs identified.

### Stage 4 — V1.1 secure personalisation
Investigate accounts, persistent profiles, actions, reminders and consent. Gate: approved threat model, privacy/security design, storage/deletion tests and appropriate compliance review before real data.

### Stage 5 — Public beta
Small controlled cohort with non-sensitive data; accessibility/security/usability/policy checks. Gate: zero critical policy defects, agreed usability targets, support and rollback procedure.

## 8. Development operating agreement
- One work package at a time, each linked to requirement IDs and named acceptance tests.
- Inspect current repository state and outstanding PRs before coding.
- State **in scope, out of scope, changed files, tests, manual validation and rollback**.
- No wholesale rewrite or framework migration without separate approval.
- No new claims/policy references without source verification.
- No merges, live deploys or secret changes without explicit approval.
- Record unresolved risks rather than silently assuming success.
- Freeze new features while a release is in acceptance testing.
- A feature is done only after requirements, tests, UI, source review (where relevant), privacy/security checks, docs and PR approval.

## 9. Open decisions (do not guess)
1. Exact first 3–5 entitlement scenarios and reviewer for JSP interpretation.
2. Extent of initially supported Services, ranks and pension schemes.
3. Whether public beta runs entirely in anonymous demo mode.
4. Hosting, privacy notices and data protection responsibilities before accounts.
5. Which JPA UI steps can be verified from permitted, current non-sensitive screenshots or authorised documentation.
6. Measured performance test environment and beta usability recruitment.

**Scope authority:** This document guides future work but never overrides official MOD instructions or legislation.