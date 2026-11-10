# Forces HQ — Requirements and Acceptance Test Matrix 1.0
**Status:** Proposed verification plan, not evidence that a requirement is implemented.  
**Date:** 10 November 2026  
**Legend:** U = unverified/not yet assessed; P = proposed test; existing tests must be independently checked. Only mark PASS with linked evidence.

| ID | Requirement | Minimum test / acceptance evidence | Stage | Current state |
|---|---|---|---|---|
| FHQ-01.1 | Persistent section navigation | Navigate all nine existing sections, including scroll; no section inaccessible | 1 | U; Phase 1 branch reports implementation |
| FHQ-01.2 | Responsive dashboard | Android 360/390px and desktop; no overflow; usable touch and keyboard navigation | 1 | U |
| FHQ-01.3 | Relevant personalised tiles | Change permitted profile parameters; only appropriately relevant suggestions change; none assert guaranteed eligibility | 3 | P |
| FHQ-02.1 | Validated service profile | Reject inconsistent enlistment/birth/exit dates, unsupported combinations, preserve prior valid profile | 1/3 | U; Phase 1 tests reported |
| FHQ-02.2 | Profile propagation | Update rank/service and see each dependent supported module update with no stale values | 3 | P |
| FHQ-02.3 | Explicit unknown values | Missing dates/scheme/rank never inferred; user gets explanatory prompt | 3 | P |
| FHQ-03.1 | Policy source catalogue | Every verified entry has original source URL, publisher, edition, effective/review dates and locator | 2 | P |
| FHQ-03.2 | Source accuracy | Reviewer compares every claimed paragraph and critical exception with official edition; 100% match | 2 | P |
| FHQ-03.3 | Abstention | Test missing/contradictory/out-of-scope policy; no fictitious paragraph or definitive claim | 2 | P |
| FHQ-03.4 | Superseded publication | Mark source superseded; user sees warning and no stale definite advice | 2 | P |
| FHQ-04.1 | Guided claim questions | For each pilot scenario, cover qualifying, disqualifying, missing-data and exception cases | 2 | P |
| FHQ-04.2 | Explainable assessment | Show conditions and sources contributing to potential/negative/undetermined outcome | 2 | P |
| FHQ-04.3 | JPA walkthrough | Validate each on-screen step against allowed current evidence; otherwise label guidance unverified | 2 | P |
| FHQ-04.4 | Factual claim justification | Check generated text against supplied facts; verify any length requirement; never fabricate evidence | 2 | P |
| FHQ-04.5 | No false submission | UI never says claim submitted, approved or paid | 2 | P |
| FHQ-05.1 | Dated pay tables | Independent reference tests for each advertised Service/rank/level/date | 3 | P |
| FHQ-05.2 | Pension and EDP accuracy | Test cases across each supported scheme, transition rule, boundary and incomplete history | 3 | P |
| FHQ-05.3 | Honest scenario results | Display scheme, assumptions, scope, rounding, version and official forecast route | 3 | P |
| FHQ-06.1 | Career CRUD | Add, modify, remove, export non-sensitive example; changes persist within declared session | 1/3 | U |
| FHQ-06.2 | No invented evidence | Draft only includes user-provided verified/fictional practice details; editable and explicitly unofficial | 1/3 | U |
| FHQ-07.1 | Military life checklists | Assignment, leave, accommodation and family scenarios show official links and conditional caveats | 3 | P |
| FHQ-08.1 | Privacy disclosures | Independent-app notice, no MOD access claim, permitted-data warning, real retention period stated | 1 | U |
| FHQ-08.2 | Accounts/storage gate | Prior to storing real user data: threat model, DPA/GDPR review, access controls, encryption, delete/export tests | 4 | P |
| NFR-01 | No regressions | 100% applicable automated suite passing; zero release-blocking defects | Each | U |
| NFR-02 | Real-device smoke test | Actual Android tested for navigation, forms, readability and session behavior | 1 and each release | U |
| NFR-03 | Accessibility | WCAG 2.2 AA target; automated and manual keyboard/contrast/form tests | 5 | P |
| NFR-04 | Performance | Record hardware/network, run repeatable test, primary interactions target <3 seconds excluding external dependencies | 5 | P |
| NFR-05 | Beta usability | >=90% independent completion on prespecified tasks, zero critical policy errors | 5 | P |
| GOV-01 | Release discipline | Scoped PR with tests, linked IDs, docs, reviewer sign-off and rollback instructions | Each | P |
| GOV-02 | No unauthorised deployment | Branch review; no merge or live deploy without explicit approval | Each | P |

## Stage 2 sample decision-table test pattern
For **each** verified scenario, the reviewer supplies the policy source, effective date, exact rule/exception and expected result. Example classes:
1. All required qualifying facts true → potentially eligible, with accurate conditions.
2. An explicit exclusion applies → not indicated, cite exact exclusion.
3. Missing critical fact → cannot determine, ask only for that information.
4. Unverified source or stale policy → cannot determine and flag review.
5. Conflicting sources → cannot determine and escalate.
6. Claim preparation → user-provided facts only, evidence checklist, no submission claim.

**Never fill expected monetary amounts or eligibility solely from assumptions.**

## Phase gates / verification evidence
- **Stage 0:** product spec and this matrix present; stakeholder review recorded.
- **Stage 1:** test command/output, Android screen recordings/screenshots, scoped PR diff, fallback plan.
- **Stage 2:** policy review worksheet per scenario; screenshots/links for source, dated citations, decision-case test results and reviewer.
- **Stage 3:** reference model workbook/test fixtures, official source links and calculation tolerance.
- **Stage 4:** reviewed security/privacy documents plus operational tests.
- **Stage 5:** task-by-task anonymised usability results, issues and acceptance sign-off.

## Working template for each Codex task
- Requirement IDs:
- Problem / user task:
- In scope:
- Explicit exclusions:
- Files/modules permitted to change:
- Source/reviewer required:
- Automated test names:
- Manual acceptance on Android:
- Expected artifacts:
- Rollback path:
- Definition of done:

**No implementation work authorised by this document alone.**